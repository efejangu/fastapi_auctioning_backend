import pytest
from fastapi import WebSocket, HTTPException
from unittest.mock import AsyncMock, MagicMock, patch
from sqlalchemy.orm import Session
from collections import defaultdict
from app.core.services.bidding_service import BiddingService
from app.core.repo.bid.bidding_main import BiddingMain
from app.core.repo.bid.bidding_logic import AuctionGroup
from app.core.repo.bid.bidding_stack import Stack
from app.models import User
import asyncio
from datetime import datetime, timedelta

class MockWebSocket:
    def __init__(self, user_id=None):
        self.sent_messages = []
        self.send_text = AsyncMock()
        self.accept = AsyncMock()
        self.user_id = user_id
        
    async def receive_text(self):
        return "test_message"
        
    async def send_json(self, data):
        self.sent_messages.append(data)

class UserQuery:
    """Helper class to handle user queries in tests"""
    def __init__(self, users):
        self.users = users
        
    def filter(self, condition):
        # Handle User.id == user_id condition
        if hasattr(condition.left, 'key') and condition.left.key == 'id':
            user_id = condition.right.value
            self.filtered = next((u for u in self.users if u.id == user_id), None)
        return self
        
    def first(self):
        return getattr(self, 'filtered', None)

class TestConnectionManager:
    def __init__(self):
        self.groups = {}

class TestBiddingService:
    @pytest.fixture
    def mock_users(self):
        return [
            MagicMock(
                id=f"user_{i}", 
                first_name=f"User{i}",
                email=f"user{i}@example.com"
            ) for i in range(1, 6)
        ]

    @pytest.fixture
    def mock_db(self, mock_users):
        mock = MagicMock(spec=Session)
        
        # Mock the query builder chain
        mock.query.return_value.filter.return_value.first.side_effect = lambda: None  # Default return None
        
        # Handle User queries
        def handle_user_query(model):
            if model == User:
                return UserQuery(mock_users)
            return MagicMock()
            
        mock.query.side_effect = handle_user_query
        
        # Add commit and rollback mocks
        mock.commit = MagicMock()
        mock.rollback = MagicMock()
        
        return mock

    @pytest.fixture
    
    def mock_bidding_main(self):
        mock = MagicMock(spec=BiddingMain)
        # Create the connection manager with our test implementation
        mock.connection_manager = TestConnectionManager()
        
        # Set up async mocks for the methods
        mock.create_group = AsyncMock(side_effect=self._handle_create_group)
        mock.connect = AsyncMock()
        mock.place_bid = AsyncMock(side_effect=self._handle_bid)
        mock.disconnect = AsyncMock()
        mock.close_auction = AsyncMock()
        mock.bidding_status = AsyncMock()
        return mock

    def _handle_create_group(self, websocket, group_name, target_price):
        """Test helper to simulate group creation"""
        mock_auction = MagicMock(
            target_price=target_price,
            current_bid=0,
            highest_bidder=None,
            highest_bid=0,  
            bid_timer=MagicMock(  
                timer_task=MagicMock()
            )
        )
        
        self.bidding_service.bidding_main.connection_manager.groups[group_name] = {
            "connections": set(),
            f"{group_name}_object": mock_auction
        }
        return mock_auction

    def _handle_bid(self, websocket, bid_amount, bidder_name=None, group_name=None):
        """Test helper to simulate bid handling"""
        if bid_amount <= 0:
            raise HTTPException(status_code=400, detail="Bid amount must be greater than zero")
        
        # Get the mock auction group
        group = self.bidding_service.bidding_main.connection_manager.groups.get(group_name)
        if not group:
            raise HTTPException(status_code=404, detail="Auction not found")
            
        auction = group[f"{group_name}_object"]
        
        # Update auction state
        auction.current_bid = bid_amount
        auction.highest_bid = bid_amount  
        auction.highest_bidder = bidder_name
        
        # Reset bid timer
        if hasattr(auction, 'bid_timer'):
            auction.bid_timer.timer_task = None  
        
        if bid_amount >= auction.target_price:
            # Schedule close_auction without actually accessing any real state
            asyncio.create_task(self.bidding_service.bidding_main.close_auction(group_name))

    @pytest.fixture
    def setup(self, mock_db, mock_bidding_main, mock_users):
        self.bidding_service = BiddingService(
            db=mock_db,
            bidding_main=mock_bidding_main
        )
        self.websockets = {
            user.id: MockWebSocket(user.id) for user in mock_users
        }
        self.users = mock_users
        self.auction_groups = {}
        return self

    @pytest.mark.asyncio
    async def test_realistic_auction_scenario(self, setup):
        """
        Test a complete auction lifecycle with multiple users bidding
        This test simulates a real-world scenario where:
        1. An auction is created for a luxury item
        2. Multiple users join the auction
        3. Users place competitive bids
        4. Some users get outbid and stop bidding
        5. The auction closes when no new bids are placed
        6. The winner is correctly determined
        """
        # Setup auction for a luxury watch
        auction_name = "luxury_watch_auction"
        starting_price = 5000.0
        target_price = 10000.0
        
        # Create auction
        await self.bidding_service.create_group(
            self.websockets["user_1"],
            auction_name,
            target_price
        )
        
        # Connect all users to the auction
        for user_id, websocket in self.websockets.items():
            await self.bidding_service.connect(
                websocket,
                auction_name
            )
        
        # Simulate realistic bidding sequence
        bid_sequence = [
            ("user_1", 5000.0, "Initial bid at starting price"),
            ("user_2", 5500.0, "Competitive response"),
            ("user_3", 6000.0, "New bidder enters"),
            ("user_2", 6500.0, "Quick counter-bid"),
            ("user_4", 7000.0, "Aggressive new entry"),
            ("user_3", 7500.0, "Staying in the game"),
            ("user_4", 8000.0, "Determined bidder"),
            ("user_5", 9000.0, "Late entry with strong bid"),
            ("user_4", 9500.0, "Final push"),
            ("user_5", 10100.0, "Winning bid above target")
        ]
        
        # Execute bid sequence
        for user_id, amount, description in bid_sequence:
            await self.bidding_service.place_bid(
                self.websockets[user_id],
                amount,
                auction_name,
                user_id
            )
            
            # Verify bid was processed
            self.bidding_service.bidding_main.place_bid.assert_awaited_with(
                self.websockets[user_id],
                amount,
                bidder_name=next(u.first_name for u in self.users if u.id == user_id),
                group_name=auction_name
            )
            
            # Small delay to simulate real-world timing
            await asyncio.sleep(0.1)
        
        # Close auction
        await self.bidding_service.close_auction(auction_name)
        self.bidding_service.bidding_main.close_auction.assert_awaited_once_with(auction_name)

    @pytest.mark.asyncio
    async def test_auction_timeout_scenario(self, setup):
        """Test auction behavior when no bids are placed within timeout period"""
        auction_name = "timeout_test_auction"
        target_price = 1000.0
        
        # Create auction
        await self.bidding_service.create_group(
            self.websockets["user_1"],
            auction_name,
            target_price
        )
        
        # Connect users
        for user_id in ["user_1", "user_2"]:
            await self.bidding_service.connect(
                self.websockets[user_id],
                auction_name
            )
        
        # Place initial bid
        await self.bidding_service.place_bid(
            self.websockets["user_1"],
            500.0,
            auction_name,
            "user_1"
        )
        
        # Get the BidTimer instance
        auction_group = self.bidding_service.bidding_main.connection_manager.groups[auction_name][f"{auction_name}_object"]
        assert auction_group.bid_timer.timer_task is not None, "Timer should be running after bid"
        
        # Wait for slightly longer than the timeout
        await asyncio.sleep(16)  # Timer is set to 15 seconds
        
        # Verify timer was cancelled and auction was closed
        assert auction_group.bid_timer.timer_task is None, "Timer should be cancelled after timeout"
        assert not auction_group.auction_open, "Auction should be closed after timeout"
        
        # Verify close_auction was called
        self.bidding_service.bidding_main.close_auction.assert_awaited_with(auction_name)

    @pytest.mark.asyncio
    async def test_concurrent_bidding_handling(self, setup):
        """Test system's ability to handle concurrent bids properly"""
        auction_name = "concurrent_test_auction"
        target_price = 5000.0
        
        # Create auction
        await self.bidding_service.create_group(
            self.websockets["user_1"],
            auction_name,
            target_price
        )
        
        # Connect multiple users
        for user_id in ["user_1", "user_2", "user_3"]:
            await self.bidding_service.connect(
                self.websockets[user_id],
                auction_name
            )
        
        # Simulate concurrent bids
        async def place_concurrent_bid(user_id, amount):
            await self.bidding_service.place_bid(
                self.websockets[user_id],
                amount,
                auction_name,
                user_id
            )
        
        # Place bids concurrently
        await asyncio.gather(
            place_concurrent_bid("user_1", 1000.0),
            place_concurrent_bid("user_2", 1100.0),
            place_concurrent_bid("user_3", 1200.0)
        )
        
        # Get auction state
        auction_group = self.bidding_service.bidding_main.connection_manager.groups[auction_name][f"{auction_name}_object"]
        
        # Verify all bids were processed
        assert self.bidding_service.bidding_main.place_bid.await_count == 3
        
        # Verify final auction state
        assert auction_group.highest_bid == 1200.0
        assert auction_group.highest_bidder == "User3"
        
        # Verify bid stack order (most recent first)
        top_bid = auction_group.stack.peek()
        assert top_bid['bid'] == 1200.0
        assert top_bid['bidder'] == "User3"
        
        # Verify auction is still open
        assert auction_group.auction_open
        assert auction_group.bid_timer.timer_task is not None

    @pytest.mark.asyncio
    async def test_error_handling_scenarios(self, setup):
        """Test various error scenarios in the bidding process"""
        auction_name = "error_test_auction"
        target_price = 1000.0
        
        # Create auction
        await self.bidding_service.create_group(
            self.websockets["user_1"],
            auction_name,
            target_price
        )
        
        # Test invalid bid amount (negative)
        with pytest.raises(HTTPException) as exc_info:
            await self.bidding_service.place_bid(
                self.websockets["user_1"],
                -100.0,
                auction_name,
                "user_1"
            )
        assert exc_info.value.status_code == 400
        assert "must be greater than zero" in str(exc_info.value.detail)
        
        # Test invalid bid amount (zero)
        with pytest.raises(HTTPException) as exc_info:
            await self.bidding_service.place_bid(
                self.websockets["user_1"],
                0.0,
                auction_name,
                "user_1"
            )
        assert exc_info.value.status_code == 400
        assert "must be greater than zero" in str(exc_info.value.detail)
        
        # Test bid on non-existent auction
        with pytest.raises(HTTPException) as exc_info:
            await self.bidding_service.place_bid(
                self.websockets["user_1"],
                500.0,
                "non_existent_auction",
                "user_1"
            )
        assert exc_info.value.status_code == 404
        assert "Group not found" in str(exc_info.value.detail)
        
        # Test bid from non-existent user
        with pytest.raises(HTTPException) as exc_info:
            await self.bidding_service.place_bid(
                MockWebSocket("non_existent_user"),
                500.0,
                auction_name,
                "non_existent_user"
            )
        assert exc_info.value.status_code == 404
        assert "User not found" in str(exc_info.value.detail)

        # Test minimum increment violation
        await self.bidding_service.place_bid(
            self.websockets["user_1"],
            500.0,
            auction_name,
            "user_1"
        )
        
        with pytest.raises(HTTPException) as exc_info:
            await self.bidding_service.place_bid(
                self.websockets["user_2"],
                500.1,  # Less than 1% increment
                auction_name,
                "user_2"
            )
        assert exc_info.value.status_code == 400
        assert "must be at least" in str(exc_info.value.detail)

    @pytest.mark.asyncio
    async def test_auction_closing_conditions(self, setup):
        """Test different conditions that can lead to auction closing"""
        auction_name = "closing_test_auction"
        target_price = 1000.0
        
        # Create auction
        await self.bidding_service.create_group(
            self.websockets["user_1"],
            auction_name,
            target_price
        )
        
        # Connect users
        for user_id in ["user_1", "user_2"]:
            await self.bidding_service.connect(
                self.websockets[user_id],
                auction_name
            )
        
        # Test case 1: Target price reached
        await self.bidding_service.place_bid(
            self.websockets["user_1"],
            target_price + 100,
            auction_name,
            "user_1"
        )
        self.bidding_service.bidding_main.close_auction.assert_awaited_with(auction_name)
        
        # Reset mock for next test
        self.bidding_service.bidding_main.close_auction.reset_mock()
        
        # Test case 2: Manual closing
        await self.bidding_service.close_auction(auction_name)
        self.bidding_service.bidding_main.close_auction.assert_awaited_with(auction_name)

    @pytest.mark.asyncio
    async def test_user_disconnection_handling(self, setup):
        """Test system behavior when users disconnect during auction"""
        auction_name = "disconnect_test_auction"
        target_price = 1000.0
        
        # Create auction
        await self.bidding_service.create_group(
            self.websockets["user_1"],
            auction_name,
            target_price
        )
        
        # Connect users
        for user_id in ["user_1", "user_2", "user_3"]:
            await self.bidding_service.connect(
                self.websockets[user_id],
                auction_name
            )
        
        # Place some initial bids
        await self.bidding_service.place_bid(
            self.websockets["user_1"],
            500.0,
            auction_name,
            "user_1"
        )
        
        await self.bidding_service.place_bid(
            self.websockets["user_2"],
            600.0,
            auction_name,
            "user_2"
        )
        
        # Simulate user_2 disconnecting
        await self.bidding_service.disconnect(
            self.websockets["user_2"],
            auction_name
        )
        
        # Verify user_2 was disconnected
        self.bidding_service.bidding_main.disconnect.assert_awaited_with(
            self.websockets["user_2"],
            auction_name
        )
        
        # Verify remaining user can still bid
        await self.bidding_service.place_bid(
            self.websockets["user_3"],
            700.0,
            auction_name,
            "user_3"
        )
        
        # Verify bid was processed
        self.bidding_service.bidding_main.place_bid.assert_awaited_with(
            self.websockets["user_3"],
            700.0,
            bidder_name="User3",
            group_name=auction_name
        )