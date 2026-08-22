class ConfidenceScorer:

    @staticmethod
    def calculate(frequency):

        if frequency >= 5:
            return 0.99

        elif frequency >= 3:
            return 0.90

        elif frequency >= 2:
            return 0.80

        return 0.70