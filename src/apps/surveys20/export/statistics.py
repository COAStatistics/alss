import os
import pandas
from django.db.models import Sum, Count
from django.conf import settings
from openpyxl import load_workbook

from apps.surveys20.models import Lack, Survey, FarmerStat, PRODUCT_TYPE_CHOICES


class StatisticsExporter:

    def __init__(self):
        template = os.path.join(settings.BASE_DIR, 'apps/surveys20/export/statistics_template.xlsx')
        self.wb = load_workbook(filename=template)
        self.sheet1 = self.wb['表5 (發布版)']
        self.sheet2 = self.wb['表3(對內版)']
        self.sheet3 = self.wb['表6 (發布版)']
        self.sheet4 = self.wb['表6 (對內版)']
        self.survey_qs = Survey.objects.filter(readonly=False).exclude(note__icontains='無效戶')
        self.magnification_factor_map = {
            obj.survey.farmer_id: obj.stratify.magnification_factor
            for obj in FarmerStat.objects.all()
        }
        self.survey_map = {
            survey.farmer_id: survey
            for survey in Survey.objects.prefetch_related(
                'farm_location', 'farm_location__code', 'management_types', 'lacks'
            ).filter(readonly=False, page=1)
        }
        self.lack_farmer_ids = Lack.objects.get(id=3).surveys.filter(readonly=False).values_list('farmer_id', flat=True)

    def get_sheet_1_3_rows(self, sheet_idx, farmer_id):
        mapping = {
            1: [8, 9, 11, 12, 13, 14],
            3: [9, 10, 12, 13, 14, 15]
        }
        add_target_rows = []
        rows = mapping.get(sheet_idx)

        survey = self.survey_map.get(farmer_id)
        product_type = survey.management_types.first().type
        region = survey.farm_location.code.region

        if product_type == PRODUCT_TYPE_CHOICES.crop:
            add_target_rows.append(rows[0])
        elif product_type == PRODUCT_TYPE_CHOICES.animal:
            add_target_rows.append(rows[1])

        if region == 1:
            add_target_rows.append(rows[2])
        elif region == 2:
            add_target_rows.append(rows[3])
        elif region == 3:
            add_target_rows.append(rows[4])
        elif region == 4:
            add_target_rows.append(rows[5])

        return add_target_rows

    def get_sheet_2_4_rows(self, sheet_idx, farmer_id):
        survey = self.survey_map.get(farmer_id)
        management_type = survey.management_types.first()
        crop_mapping = {1: 8, 2: 9, 3: 11, 4: 10, 5: 12, 6: 13, 7: 14, 8: 16, 9: 16, 10: 15}
        animal_mapping = {11: 18, 12: 19, 13: 20, 14: 21}
        if management_type.id in crop_mapping.keys():
            rows = [7, crop_mapping.get(management_type.id)]
        elif management_type.id in animal_mapping.keys():
            rows = [17, animal_mapping.get(management_type.id)]
        else:
            rows = []
        if sheet_idx == 4:
            rows = [i + 1 for i in rows]
        return rows

    def process_is_hire(self):
        for farmer_id, factor in self.magnification_factor_map.items():
            survey = self.survey_map.get(farmer_id)
            column = 'D' if survey.hire else 'C'
            for row in self.get_sheet_1_3_rows(1, farmer_id):
                cell_value = self.sheet1[f'{column}{row}'].value or 0
                self.sheet1[f'{column}{row}'] = cell_value + 1 * factor
            for row in self.get_sheet_2_4_rows(2, farmer_id):
                cell_value = self.sheet2[f'{column}{row}'].value or 0
                self.sheet2[f'{column}{row}'] = cell_value + 1 * factor

    def process_is_lack(self):
        for farmer_id, factor in self.magnification_factor_map.items():
            survey = self.survey_map.get(farmer_id)
            lack = survey.lacks.first()
            column = 'D' if lack.is_lack else 'C'
            for row in self.get_sheet_1_3_rows(3, farmer_id):
                cell_value = self.sheet3[f'{column}{row}'].value or 0
                self.sheet3[f'{column}{row}'] = cell_value + 1 * factor
            # sheet 4
            is_lack_column_map = {1: 'DC', 2: 'EC', 3: 'F', 4: 'C'}
            for column in is_lack_column_map.get(lack.id):
                for row in self.get_sheet_2_4_rows(4, farmer_id):
                    cell_value = self.sheet4[f'{column}{row}'].value or 0
                    self.sheet4[f'{column}{row}'] = cell_value + 1 * factor

    def process_long_term_hires(self):
        """Modify sheet 1 column G, E; sheet 3 column G, E"""

        qs = self.survey_qs.prefetch_related(
            'long_term_hires', 'long_term_hires__number_workers',
        ).values('farmer_id').annotate(
            sum_workers=Sum('long_term_hires__number_workers__count'),
        )

        for result in qs:
            farmer_id = result['farmer_id']

            factor = self.magnification_factor_map[farmer_id]
            sum_workers = result['sum_workers'] * factor if result['sum_workers'] else 0

            if sum_workers:
                for row in self.get_sheet_1_3_rows(1, farmer_id):
                    cell_value = self.sheet1[f'E{row}'].value or 0
                    self.sheet1[f'E{row}'] = cell_value + 1 * factor
                    cell_value = self.sheet1[f'G{row}'].value or 0
                    self.sheet1[f'G{row}'] = cell_value + sum_workers
                for row in self.get_sheet_2_4_rows(2, farmer_id):
                    cell_value = self.sheet2[f'E{row}'].value or 0
                    self.sheet2[f'E{row}'] = cell_value + 1 * factor
                    cell_value = self.sheet2[f'G{row}'].value or 0
                    self.sheet2[f'G{row}'] = cell_value + sum_workers

    def process_long_term_lacks(self):
        """Modify sheet 3 column E, G; sheet 4 G, I"""

        qs = self.survey_qs.prefetch_related(
            'long_term_lacks',
        ).filter(farmer_id__in=self.lack_farmer_ids).values('farmer_id').annotate(
            sum_workers=Sum('long_term_lacks__count'),
        )

        for result in qs:
            farmer_id = result['farmer_id']

            factor = self.magnification_factor_map[farmer_id]
            sum_workers = result['sum_workers'] * factor if result['sum_workers'] else 0

            if sum_workers:
                for row in self.get_sheet_1_3_rows(3, farmer_id):
                    cell_value = self.sheet3[f'E{row}'].value or 0
                    self.sheet3[f'E{row}'] = cell_value + 1 * factor
                    cell_value = self.sheet3[f'G{row}'].value or 0
                    self.sheet3[f'G{row}'] = cell_value + sum_workers
                for row in self.get_sheet_2_4_rows(4, farmer_id):
                    cell_value = self.sheet4[f'G{row}'].value or 0
                    self.sheet4[f'G{row}'] = cell_value + 1 * factor
                    cell_value = self.sheet4[f'I{row}'].value or 0
                    self.sheet4[f'I{row}'] = cell_value + sum_workers

    def process_short_term_hires(self):
        """Modify sheet 1 column H, F; sheet 2 column F, H"""

        qs = self.survey_qs.prefetch_related(
            'short_term_hires', 'short_term_hires__number_workers',
        ).values('farmer_id').annotate(
            sum_workers=Sum('short_term_hires__number_workers__count'),
        )

        for result in qs:
            farmer_id = result['farmer_id']

            factor = self.magnification_factor_map[farmer_id]
            sum_workers = result['sum_workers'] * factor if result['sum_workers'] else 0

            if sum_workers:
                for row in self.get_sheet_1_3_rows(1, farmer_id):
                    cell_value = self.sheet1[f'F{row}'].value or 0
                    self.sheet1[f'F{row}'] = cell_value + 1 * factor
                    cell_value = self.sheet1[f'H{row}'].value or 0
                    self.sheet1[f'H{row}'] = cell_value + sum_workers
                for row in self.get_sheet_2_4_rows(2, farmer_id):
                    cell_value = self.sheet2[f'F{row}'].value or 0
                    self.sheet2[f'F{row}'] = cell_value + 1 * factor
                    cell_value = self.sheet2[f'H{row}'].value or 0
                    self.sheet2[f'H{row}'] = cell_value + sum_workers

    def process_short_term_lacks(self):
        """Modify sheet 3 column H, F, sheet 4 column H, J"""

        qs = self.survey_qs.prefetch_related(
            'short_term_lacks',
        ).filter(farmer_id__in=self.lack_farmer_ids).values('farmer_id', 'short_term_lacks__count').annotate(
            month_count=Count('short_term_lacks__months'),
        ).filter(month_count__gte=1)

        df = pandas.DataFrame(list(qs))
        df['workers'] = df['short_term_lacks__count'] * df['month_count']
        df = df.groupby('farmer_id', as_index=False).agg({'workers': 'sum'})

        for _, result in df.iterrows():
            farmer_id = result['farmer_id']

            factor = self.magnification_factor_map[farmer_id]
            sum_workers = result['workers'] * factor if result['workers'] else 0

            if sum_workers:
                for row in self.get_sheet_1_3_rows(3, farmer_id):
                    cell_value = self.sheet3[f'F{row}'].value or 0
                    self.sheet3[f'F{row}'] = cell_value + 1 * factor
                    cell_value = self.sheet3[f'H{row}'].value or 0
                    self.sheet3[f'H{row}'] = cell_value + sum_workers
                for row in self.get_sheet_2_4_rows(4, farmer_id):
                    cell_value = self.sheet4[f'H{row}'].value or 0
                    self.sheet4[f'H{row}'] = cell_value + 1 * factor
                    cell_value = self.sheet4[f'J{row}'].value or 0
                    self.sheet4[f'J{row}'] = cell_value + sum_workers

    def process_no_salary_hires(self):
        """Modify sheet 1 column I"""

        qs = self.survey_qs.prefetch_related(
            'no_salary_hires',
        ).values('farmer_id').annotate(
            sum_workers=Sum('no_salary_hires__count'),
        )

        for result in qs:
            farmer_id = result['farmer_id']

            factor = self.magnification_factor_map[farmer_id]
            sum_workers = result['sum_workers'] * factor if result['sum_workers'] else 0

            if sum_workers:
                for row in self.get_sheet_1_3_rows(1, farmer_id):
                    cell_value = self.sheet1[f'I{row}'].value or 0
                    self.sheet1[f'I{row}'] = cell_value + sum_workers
                for row in self.get_sheet_2_4_rows(2, farmer_id):
                    cell_value = self.sheet2[f'I{row}'].value or 0
                    self.sheet2[f'I{row}'] = cell_value + sum_workers

    def __call__(self, *args, **kwargs):

        self.process_is_hire()

        self.process_long_term_hires()

        self.process_short_term_hires()

        self.process_no_salary_hires()

        self.process_is_lack()

        self.process_long_term_lacks()

        self.process_short_term_lacks()

        self.wb.save(*args, **kwargs)
