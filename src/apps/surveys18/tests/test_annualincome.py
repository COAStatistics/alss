from . import TestCase, setup_fixtures
from apps.surveys18.models import Survey, AnnualIncome, MarketType, IncomeRange


class ModelTestCase(TestCase):
    @classmethod
    def setUpTestData(cls):
        # load fixtures
        setup_fixtures()

    def test_create_annual_income(self):
        survey_id = Survey.objects.get(id=3)
        market_type_a = MarketType.objects.get(id=2)
        income_range_a = IncomeRange.objects.get(id=8)
        market_type_b = MarketType.objects.get(id=3)
        income_range_b = IncomeRange.objects.get(id=1)
        market_type_c = MarketType.objects.get(id=5)
        income_range_c = IncomeRange.objects.get(id=8)

        annual_income_list_before_size = AnnualIncome.objects.count()

        # new value
        AnnualIncome.objects.create(
            survey=survey_id, market_type=market_type_a, income_range=income_range_a
        )
        AnnualIncome.objects.create(
            survey=survey_id, market_type=market_type_b, income_range=income_range_b
        )
        AnnualIncome.objects.create(
            survey=survey_id, market_type=market_type_c, income_range=income_range_c
        )

        annual_income_list_after_size = AnnualIncome.objects.count()
        self.assertEqual(
            annual_income_list_after_size, annual_income_list_before_size + 3
        )

    def test_survey_delete(self):
        Survey.objects.filter(id=1).delete()
        annual_income_list = AnnualIncome.objects.filter(survey__id=1)
        self.assertEqual(annual_income_list.count(), 0)

    def test_survey_delete_all(self):
        market_type_list_before_size = MarketType.objects.count()
        income_range_list_before_size = len(IncomeRange.objects.all())
        Survey.objects.all().delete()
        annual_income_list = AnnualIncome.objects.all()
        market_type_list_after_size = MarketType.objects.count()
        income_range_list_after_size = len(IncomeRange.objects.all())

        self.assertEqual(len(annual_income_list), 0)
        self.assertEqual(market_type_list_after_size, market_type_list_before_size)
        self.assertEqual(income_range_list_after_size, income_range_list_before_size)
