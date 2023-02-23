from Strategy.Base_Bracket_Orders import BracketStrategy

class BuyHoldStrategy(BracketStrategy):

    # First, you define some parameters
    params = (
    )

    # Then, you initialize indicators
    def _init_indicators(self):
        pass

    # Finally, you implement your open conditions
    # Closing is done with stop loss or take profit
    def _open_long_condition(self) -> bool:
        return True

    def _open_short_condition(self) -> bool:
        pass