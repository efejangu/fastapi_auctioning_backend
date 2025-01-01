import pytest
import asyncio
from unittest.mock import AsyncMock, MagicMock, patch
from fastapi import WebSocket, HTTPException
from app.core.repo.bid.bidding_logic import AuctionGroup
from app.core.repo.bid.bidding_stack import Stack, Node
from app.core.repo.bid.bidding_watch import BidTimer
from app.core.repo.bid.conn_manager import ConnectionManager

class TestBiddingStack:
    def setup_method(self):
        self.stack = Stack()
        self.test_bid = {"bid": 100.0, "bidder": "test_user"}

    def test_push_valid_bid(self):
        size = self.stack.push(self.test_bid)
        assert size == 1
        assert self.stack.peek() == self.test_bid

    def test_push_invalid_bid(self):
        with pytest.raises(ValueError):
            self.stack.push({"invalid": "data"})

    def test_pop_from_empty_stack(self):
        assert self.stack.pop() is None

    def test_pop_from_stack_with_items(self):
        self.stack.push(self.test_bid)
        popped_bid = self.stack.pop()
        assert popped_bid == self.test_bid
        assert self.stack.size == 0

    def test_peek_empty_stack(self):
        assert self.stack.peek() is None

    def test_peek_with_items(self):
        self.stack.push(self.test_bid)
        assert self.stack.peek() == self.test_bid
        assert self.stack.size == 1  # Ensure peek doesn't remove the item

    def test_collapse_stack(self):
        self.stack.push(self.test_bid)
        self.stack.push({"bid": 200.0, "bidder": "user2"})
        self.stack.collapse()
        assert self.stack.size == 0
        assert self.stack.head is None

class TestBidTimer:
    @pytest.fixture
    def callback(self):
        return AsyncMock()

    @pytest.fixture
    def bid_timer(self, callback):
        return BidTimer(timeout=1, callback=callback)

    @pytest.mark.asyncio
    async def test_timer_start(self, bid_timer):
        await bid_timer.start()
        assert bid_timer.timer_task is not None
        assert not bid_timer.timer_task.done()
        bid_timer.stop()

    @pytest.mark.asyncio
    async def test_timer_stop(self, bid_timer):
        await bid_timer.start()
        bid_timer.stop()
        assert bid_timer.timer_task is None

    @pytest.mark.asyncio
    async def test_timer_callback(self, bid_timer, callback):
        await bid_timer.start()
        await asyncio.sleep(1.1)  # Wait for timer to expire
        callback.assert_called_once()

    @pytest.mark.asyncio
    async def test_timer_restart(self, bid_timer):
        await bid_timer.start()
        first_task = bid_timer.timer_task
        await bid_timer.start()  # Restart timer
        assert bid_timer.timer_task is not None
        assert bid_timer.timer_task != first_task
        bid_timer.stop()

class TestConnectionManager:
    @pytest.fixture
    def connection_manager(self):
        return ConnectionManager()

    @pytest.fixture
    def websocket(self):
        mock_ws = AsyncMock(spec=WebSocket)
        mock_ws.send_text = AsyncMock()
        return mock_ws

    @pytest.mark.asyncio
    async def test_connect_to_nonexistent_group(self, connection_manager, websocket):
        with pytest.raises(ValueError):
            await connection_manager.connect(websocket, "nonexistent_group")

    @pytest.mark.asyncio
    async def test_broadcast_message(self, connection_manager, websocket):
        group_name = "test_group"
        connection_manager.groups[group_name] = {"connections": {websocket}}
        await connection_manager.broadcast("test message", group_name)
        websocket.send_text.assert_called_once_with("test message")

    @pytest.mark.asyncio
    async def test_disconnect_all(self, connection_manager, websocket):
        group_name = "test_group"
        connection_manager.groups[group_name] = {"connections": {websocket}}
        await connection_manager.disconnect_all(group_name)
        assert group_name not in connection_manager.groups

    @pytest.mark.asyncio
    async def test_get_group_count(self, connection_manager, websocket):
        group_name = "test_group"
        connection_manager.groups[group_name] = {"connections": {websocket}}
        count = await connection_manager.get_group_count(group_name)
        assert count == 1

class TestAuctionGroup:
    @pytest.fixture
    def connection_manager(self):
        return MagicMock(spec=ConnectionManager)

    @pytest.fixture
    def auction_group(self, connection_manager):
        return AuctionGroup("test_auction", connection_manager, target_price=1000.0)

    @pytest.fixture
    def websocket(self):
        mock_ws = AsyncMock(spec=WebSocket)
        return mock_ws

    @pytest.mark.asyncio
    async def test_place_valid_bid(self, auction_group, websocket):
        await auction_group.place_bid(websocket, 500.0, "bidder1")
        assert auction_group.highest_bid == 500.0
        assert auction_group.highest_bidder == "bidder1"

    @pytest.mark.asyncio
    async def test_place_bid_below_minimum_increment(self, auction_group, websocket):
        await auction_group.place_bid(websocket, 500.0, "bidder1")
        await auction_group.place_bid(websocket, 500.1, "bidder2")  # Below 1% increment
        assert auction_group.highest_bidder == "bidder1"  # Bid should be rejected

    @pytest.mark.asyncio
    async def test_place_bid_after_auction_closed(self, auction_group, websocket):
        auction_group.auction_open = False
        await auction_group.place_bid(websocket, 500.0, "bidder1")
        websocket.send_text.assert_called_with("Auction is closed. No more bids can be placed.")

    @pytest.mark.asyncio
    async def test_check_target_price_reached(self, auction_group):
        auction_group.highest_bid = 1100.0  # Above target price
        await auction_group.check_target_price()
        assert not auction_group.auction_open

    @pytest.mark.asyncio
    async def test_close_auction(self, auction_group):
        auction_group.highest_bid = 900.0
        auction_group.highest_bidder = "winner"
        await auction_group.close_auction()
        assert not auction_group.auction_open
        auction_group.connection_manager.broadcast.assert_called()

@pytest.mark.asyncio
class TestRealWorldScenarios:
    @pytest.fixture
    def setup_auction(self):
        connection_manager = ConnectionManager()
        auction = AuctionGroup("luxury_watch", connection_manager, target_price=10000.0)
        return auction, connection_manager

    async def test_competitive_bidding_scenario(self, setup_auction):
        auction, _ = setup_auction
        websocket1 = AsyncMock(spec=WebSocket)
        websocket2 = AsyncMock(spec=WebSocket)
        websocket3 = AsyncMock(spec=WebSocket)

        # Initial bid
        await auction.place_bid(websocket1, 5000.0, "bidder1")
        assert auction.highest_bid == 5000.0

        # Competitive response
        await auction.place_bid(websocket2, 5500.0, "bidder2")
        assert auction.highest_bid == 5500.0

        # Aggressive bid
        await auction.place_bid(websocket3, 7000.0, "bidder3")
        assert auction.highest_bid == 7000.0

        # Winning bid
        await auction.place_bid(websocket2, 10100.0, "bidder2")
        assert not auction.auction_open  # Auction should close after target price is exceeded

    async def test_auction_timeout_scenario(self, setup_auction):
        auction, _ = setup_auction
        websocket = AsyncMock(spec=WebSocket)

        await auction.place_bid(websocket, 5000.0, "bidder1")
        await asyncio.sleep(16)  # Wait for timeout (15 seconds + 1 second buffer)
        assert auction.bid_timer.timer_task is None  # Timer should be cleared

    async def test_concurrent_bidding_scenario(self, setup_auction):
        auction, _ = setup_auction
        websockets = [AsyncMock(spec=WebSocket) for _ in range(3)]
        
        # Simulate concurrent bids
        await asyncio.gather(
            auction.place_bid(websockets[0], 5000.0, "bidder1"),
            auction.place_bid(websockets[1], 5200.0, "bidder2"),
            auction.place_bid(websockets[2], 5400.0, "bidder3")
        )

        assert auction.highest_bid == 5400.0
        assert auction.highest_bidder == "bidder3"

    async def test_error_handling_scenario(self, setup_auction):
        auction, _ = setup_auction
        websocket = AsyncMock(spec=WebSocket)

        # Test invalid bid amount
        await auction.place_bid(websocket, -100.0, "bidder1")
        websocket.send_text.assert_called_with("Bid must be greater than zero.")

        # Test bid when auction is closed
        auction.auction_open = False
        await auction.place_bid(websocket, 5000.0, "bidder1")
        assert "Auction is closed" in websocket.send_text.call_args[0][0]
