import pytest
from app.core.repo.bid.bidding_stack import Stack, Node

class TestBiddingStack:
    @pytest.fixture
    def empty_stack(self):
        return Stack()

    @pytest.fixture
    def sample_bid_data(self):
        return {"bid": 100.0, "bidder": "John"}

    def test_stack_initialization(self, empty_stack):
        assert empty_stack.size == 0
        assert empty_stack.head is None

    def test_push_valid_data(self, empty_stack, sample_bid_data):
        size = empty_stack.push(sample_bid_data)
        assert size == 1
        assert empty_stack.head.data == sample_bid_data

    def test_push_invalid_data(self, empty_stack):
        invalid_data = {"invalid": "data"}
        with pytest.raises(ValueError) as exc_info:
            empty_stack.push(invalid_data)
        assert "Data must be a dictionary with 'bid' and 'bidder' keys" in str(exc_info.value)

    def test_peek_empty_stack(self, empty_stack):
        assert empty_stack.peek() is None

    def test_peek_with_data(self, empty_stack, sample_bid_data):
        empty_stack.push(sample_bid_data)
        assert empty_stack.peek() == sample_bid_data

    def test_pop_empty_stack(self, empty_stack):
        assert empty_stack.pop() is None

    def test_pop_with_data(self, empty_stack, sample_bid_data):
        empty_stack.push(sample_bid_data)
        popped_data = empty_stack.pop()
        assert popped_data == sample_bid_data
        assert empty_stack.size == 0

    def test_multiple_push_pop_operations(self, empty_stack):
        bids = [
            {"bid": 100.0, "bidder": "John"},
            {"bid": 150.0, "bidder": "Alice"},
            {"bid": 200.0, "bidder": "Bob"}
        ]
        
        # Push all bids
        for bid in bids:
            empty_stack.push(bid)
        assert empty_stack.size == 3

        # Pop should return in LIFO order
        assert empty_stack.pop() == bids[2]  # Bob's bid
        assert empty_stack.pop() == bids[1]  # Alice's bid
        assert empty_stack.pop() == bids[0]  # John's bid
        assert empty_stack.size == 0

    def test_collapse(self, empty_stack, sample_bid_data):
        empty_stack.push(sample_bid_data)
        empty_stack.push({"bid": 150.0, "bidder": "Alice"})
        
        empty_stack.collapse()
        assert empty_stack.head is None
        assert empty_stack.size == 0

    def test_push_after_collapse(self, empty_stack, sample_bid_data):
        empty_stack.push(sample_bid_data)
        empty_stack.collapse()
        
        # Should be able to push new data after collapse
        new_bid = {"bid": 200.0, "bidder": "Bob"}
        size = empty_stack.push(new_bid)
        assert size == 1
        assert empty_stack.peek() == new_bid

  
    def test_size(self, empty_stack, sample_bid_data):
        assert empty_stack.size == 0
        empty_stack.push(sample_bid_data)
        assert empty_stack.size == 1
        empty_stack.push({"bid": 150.0, "bidder": "Alice"})
        assert empty_stack.size == 2

