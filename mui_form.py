class MUIForm:
    ALLOWED_SCHOLARSHIPS = ['Scholarship A', 'Scholarship B', 'Scholarship C']

    def __init__(self, location_name, market_dfa_name, operator, region, store_number, scholarship_name):
        self.location_name = location_name
        self.market_dfa_name = market_dfa_name
        self.operator = operator
        self.region = region
        self.store_number = store_number
        if scholarship_name not in self.ALLOWED_SCHOLARSHIPS:
            raise ValueError(f'Invalid scholarship: {scholarship_name}')
        self.scholarship_name = scholarship_name