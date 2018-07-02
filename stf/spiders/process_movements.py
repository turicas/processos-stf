import csv
import io
import os

import rows
from scrapy import Request, Spider

from stf import settings


class PtBrDateField(rows.fields.DateField):
    INPUT_FORMAT = '%d/%m/%Y'


class ProcessMovementsSpider(Spider):
    name = 'process-movements'

    def start_requests(self):
        # TODO: get filename from settings
        filename = os.path.join(settings.PROJECT_ROOT, 'data/output/lista-processos.csv')
        with open(filename, encoding='utf-8') as fobj:
            for row in csv.DictReader(fobj):
                yield Request(
                        url=row['url'],
                        method='GET',
                        meta={'process': row},
                        callback=self.parse_movements,
                )

    def parse_movements(self, response):
        process = response.request.meta['process']
        body = response.body_as_unicode()
        table = rows.import_from_html(
                io.BytesIO(body.encode('utf-8')),
                encoding='utf-8',
                index=1,
                force_types={'data': PtBrDateField},
        )
        for row in table:
            row = dict(row._asdict())
            row['numero_processo'] = process['numero_processo']
            row['classe_processo'] = process['classe_processo']
            yield row
