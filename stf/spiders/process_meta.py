import csv
import io
import os

import rows
from scrapy import Request, Spider

from stf import settings


class PtBrDateField(rows.fields.DateField):
    INPUT_FORMAT = '%d/%m/%Y'


expressoes = {
    'data_de_protocolo': '//table[@class="resultadoAndamentoProcesso"]//tr[.//span[text() = "Protocolado"]]/td[1]/span/text()',
    'data_de_distribuicao': '//table[@class="resultadoAndamentoProcesso"]//tr[.//span[text() = "Distribuído"]]/td[1]/span/text()',
    'ministro': '//table[@class="comum"]//tr[./td[text() = "Relator atual"]]/td[2]//text()',
    'origem_detalhe': '//table[@class="comum"]//tr[./td[text() = "Origem:"]]/td[2]//text()',
    'partes': '//table[@class="comum"]//tr[./td[text() != "Origem:" and text() != "Relator atual"]]/td//text()',
}


class ProcessMovementsSpider(Spider):
    name = 'process-meta'

    def start_requests(self):
        filename = os.path.join(settings.PROJECT_ROOT, 'data/output/lista-processos.csv')
        with open(filename, encoding='utf-8') as fobj:
            for row in csv.DictReader(fobj):
                yield Request(
                        url=row['url'],
                        method='GET',
                        meta={'process': row},
                        callback=self.parse_meta,
                )

    def parse_meta(self, response):
        process = response.request.meta['process']
        metadata = {
            'classe_processo': process['classe_processo'],
            'codigo_classe_processo': process['codigo_classe_processo'],
            'numero_processo': process['numero_processo'],
            'origem_ata': process['origem'],
            'procedencia_ata': process['procedencia'],
        }
        for nome, expressao in expressoes.items():
            resultado = response.xpath(expressao).extract()
            if nome == 'partes':
                partes = zip(resultado[::2], resultado[1::2])
                resultado = '|'.join(f'{tipo.strip()}: {parte.strip()}'
                                     for tipo, parte in partes)
            elif nome.startswith('data_'):
                if resultado:
                    assert len(resultado) == 1
                    resultado = PtBrDateField.deserialize(resultado[0])
            else:
                if resultado:
                    assert len(resultado) == 1
                    resultado = resultado[0]
                else:
                    resultado = None
            metadata[nome] = resultado

        yield metadata
