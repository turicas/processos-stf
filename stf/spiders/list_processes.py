import datetime
from urllib.parse import parse_qs, urljoin, urlparse

import rows
from lxml.html import document_fromstring, tostring
from scrapy import FormRequest, Request, Spider


RECORDS_BY_DATE_URL = 'http://www.stf.jus.br/portal/ataDistribuicao/listaAtaDia.asp'


def date_range(start, stop, step=None):
    if step is None:
        step = datetime.timedelta(days=1)

    current = start
    while current <= stop:
        yield current
        current += step


class ProcessesSpider(Spider):
    name = 'list-processes'
    start_date = datetime.date(2007, 1, 1)
    end_date = datetime.date(2018, 7, 1)

    def start_requests(self):
        for date in date_range(self.start_date, self.end_date):
            data = {
                    'diaAtual': '{:02d}'.format(date.day),
                    'mesAtual': '{:02d}'.format(date.month),
                    'anoAtual': str(date.year),
            }
            yield FormRequest(
                    method='POST',
                    url=RECORDS_BY_DATE_URL,
                    formdata=data,
                    meta={'date': date},
                    callback=self.parse_record_list,
            )

    def parse_record_list(self, response):
        date = response.request.meta['date']
        body = response.body_as_unicode()

        if 'Não há atas de distribuição para esta data' in body:
            yield None

        else:
            for link in response.xpath('//a/@href'):
                url = urljoin(RECORDS_BY_DATE_URL, link.extract().strip())
                if 'obterAta.asp' not in url:
                    continue

                yield Request(
                        method='GET',
                        url=url,
                        meta={
                            'date': date.strftime('%Y-%m-%d'),
                            'url': url,
                            'number': parse_qs(urlparse(url).query)['numAta'][0],
                        },
                        callback=self.parse_record_item,
                )

    def parse_record_item(self, response):
        meta = response.request.meta
        date, number = meta['date'], meta['number']
        html = response.body_as_unicode()

        for row_html in html.split('<hr')[:-1]:
            row_data = []
            for data_table in document_fromstring(row_html).xpath('//table'):
                row_data.append(data_table.xpath('./tr/td'))
            if b'ATA DA ' in tostring(row_data[0][0]):  # skip header
                row_data = row_data[1:]

            row = {
                    'data': date,
                    'numero_ata': number,
            }
            title = row_data[0]

            title_text = ' '.join(title[0].xpath('.//text()'))
            row['classe_processo'] = title_text.split('-')[0].strip()
            row['eletronico'] = 'eletrônico' in title_text.lower()

            links = rows.plugins.html.extract_links(tostring(title[0]))
            assert len(links) == 1
            row['url'] = urljoin(RECORDS_BY_DATE_URL, links[0])

            qs = parse_qs(urlparse(row['url']).query)
            row['numero_processo'] = qs['numero'][0]
            row['codigo_classe_processo'] = qs['classe'][0]
            row['recurso'] = qs['recurso'][0]
            row['tipo_julgamento'] = qs['tipoJulgamento'][0]

            for metadata in title[1:]:
                info = ' '.join(metadata.xpath('.//text()')).strip()
                assert ':' in info
                row[info[:info.find(':')].strip().lower()] = \
                        info[info.find(':') + 1:].strip()

            partes = []
            for parte in row_data[1:]:
                tipo, nome = [''.join([text.strip()
                                    for text in elem.xpath('.//text()')]).strip()
                            for elem in parte]
                partes.append('{}: {}'.format(tipo, nome))
            row['partes'] = '|'.join(partes)

            # Cleaning
            if 'relator' in row and row.get('relator', '').startswith('MIN. '):
                row['relator'] = row['relator'][5:]
            if 'proced' in row:
                row['procedencia'] = row.pop('proced')

            yield row
