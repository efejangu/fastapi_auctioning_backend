import pytest
from fastapi import WebSocket
from unittest.mock import AsyncMock, MagicMock, patch
from app.core.services.bidding_service import BiddingService
from app.core.repo.bid.bidding_main import BiddingMain
from app.core.repo.bid.bidding_logic import AuctionGroup
from app.models import User
import asyncio

class MockWebSocket:
    def __init__(self):
        self.sent_messages = []
        self.send_text = AsyncMock()

    async def receive_text(self):
        return "test_message"

class TestBiddingService:
    @pytest.fixture
    def setup(self):
        self.bidding_service = BiddingService()
        self.websocket = MockWebSocket()
        self.user_id = "test_user_123"
        self.group_name = "test_auction"
        self.target_price = 1000.0

    @pytest.mark.asyncio
    async def test_create_group_success(self, setup):
        """Test successful creation of a new bidding group"""
        with patch('app.core.repo.bid.bidding_main.BiddingMain.create_group') as mock_create:
            mock_create.return_value = None
            await self.bidding_service.create_group(
                self.websocket, 
                self.group_name, 
                self.target_price
            )
            mock_create.assert_called_once_with(
                self.websocket, 
                self.group_name, 
                self.target_price
            )

    @pytest.mark.asyncio
    async def test_place_bid_sequence(self, setup):
        """Test a sequence of bids in ascending order"""
        bids = [800.0, 850.0, 900.0]
        bidder_names = ["Alice", "Bob", "Charlie"]
        
        with patch('sqlalchemy.orm.Session') as mock_session, \
             patch('app.core.repo.bid.bidding_main.BiddingMain.place_bid') as mock_place_bid:
            
            mock_user = MagicMock()
            mock_user.first_name = "TestUser"
            mock_session.return_value.query.return_value.filter.return_value.first.return_value = mock_user
            
            for bid, bidder in zip(bids, bidder_names):
                await self.bidding_service.place_bid(
                    self.websocket,
                    bid,
                    self.group_name,
                    self.user_id
                )
                mock_place_bid.assert_called_with(
                    self.websocket,
                    bid,
                    bidder_name="TestUser",
                    group_name=self.group_name
                )

    @pytest.mark.asyncio
    async def test_auction_lifecycle(self, setup):
        """Test complete lifecycle of an auction from creation to closing"""
        # Create auction
        await self.bidding_service.create_group(
            self.websocket, 
            self.group_name, 
            self.target_price
        )
        
        # Connect bidders
        await self.bidding_service.connect(
            self.websocket,
            self.group_name
        )
        
        # Place multiple bids
        test_bids = [750.0, 800.0, 950.0, 1100.0]
        for bid in test_bids:
            await self.bidding_service.place_bid(
                self.websocket,
                bid,
                self.group_name,
                self.user_id
            )
        
        # Close auction
        await self.bidding_service.close_auction(
            self.group_name
        )
        
        # Verify final status
        status = await self.bidding_service.bidding_status(
            self.group_name
        )
        assert status is not None

    @pytest.mark.asyncio
    async def test_concurrent_bidding(self, setup):
        """Test multiple users bidding concurrently"""
        async def simulate_bid(bid_value):
            await self.bidding_service.place_bid(
                self.websocket,
                bid_value,
                self.group_name,
                self.user_id
            )

        # Create auction first
        await self.bidding_service.create_group(
            self.websocket,
            self.group_name,
            self.target_price
        )

        # Simulate concurrent bids
        await asyncio.gather(
            simulate_bid(800.0),
            simulate_bid(850.0),
            simulate_bid(900.0)
        )

    @pytest.mark.asyncio
    async def test_auction_timeout(self, setup):
        """Test auction timeout mechanism"""
        with patch('app.core.repo.bid.bidding_watch.BidTimer') as mock_timer:
            # Create auction with short timeout
            await self.bidding_service.create_group(
                self.websocket,
                self.group_name,
                self.target_price
            )
            
            # Place bid
            await self.bidding_service.place_bid(
                self.websocket,
                800.0,
                self.group_name,
                self.user_id
            )
            
            # Verify timer was started
            mock_timer.assert_called()

    @pytest.mark.asyncio
    async def test_error_conditions(self, setup):
        """Test various error conditions"""
        # Test placing bid on closed auction
        await self.bidding_service.create_group(
            self.websocket,
            self.group_name,
            self.target_price
        )
        
        await self.bidding_service.close_auction(
            self.group_name
        )
        
        with pytest.raises(Exception):
            await self.bidding_service.place_bid(
                self.websocket,
                1000.0,
                self.group_name,
                self.user_id
            )
        
        # Test invalid bid values
        with pytest.raises(ValueError):
            await self.bidding_service.place_bid(
                self.websocket,
                -100.0,  # negative bid
                self.group_name,
                self.user_id
            )

    @pytest.mark.asyncio
    async def test_realistic_auction_scenario(self, setup):
        """Test a realistic auction scenario with multiple bidders and price dynamics"""
        # Setup auction
        await self.bidding_service.create_group(
            self.websocket,
            "luxury_car_auction",
            50000.0  # target price for a luxury car
        )
        
        # Simulate multiple bidders with realistic bidding patterns
        bid_sequence = [
            (45000.0, "initial_bid"),
            (46000.0, "competitive_response"),
            (46500.0, "small_increment"),
            (48000.0, "aggressive_bid"),
            (48100.0, "minimal_increment"),
            (50500.0, "winning_bid")
        ]
        
        for bid, scenario in bid_sequence:
            with patch('sqlalchemy.orm.Session') as mock_session:
                mock_user = MagicMock()
                mock_user.first_name = f"Bidder_{scenario}"
                mock_session.return_value.query.return_value.filter.return_value.first.return_value = mock_user
                
                await self.bidding_service.place_bid(
                    self.websocket,
                    bid,
                    "luxury_car_auction",
                    self.user_id
                )
                
                # Add small delay to simulate real-world timing
                await asyncio.sleep(0.1)
        
        # Verify final auction state
        final_status = await self.bidding_service.bidding_status(
            "luxury_car_auction"
        )
        assert final_status is not None