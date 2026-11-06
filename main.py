from config.settings import CARREFOUR_BASE_URL, COOP_BASE_URL, ARQUIVO_JSON,ARQUIVO_JSON1, HTTP_TIMEOUT1, TIMEOUT, CONSULTAS, NAGUMO_BASE_URL, ARQUIVO_JSON2, HTTP_TIMEOUT2
from infra.scrapers.nagumo_scraper import NagumoScraper
from infra.scrapers.carrefour_scraper import CarrefourScraper
from infra.scrapers.coop_scraper import CoopScraper
from infra.repositories.json_repository import JsonProductRepository
from services.product_service import ProductService





def MercadoCOOP():
    scraper = CoopScraper(base_url=COOP_BASE_URL, timeout=TIMEOUT)
    repository = JsonProductRepository(ARQUIVO_JSON)
    service = ProductService(scrapers=[scraper], repository=repository)

    print("Iniciando coleta no catálogo online Coop...")
    produtos = service.coletar(CONSULTAS)
    print(f"Coleta finalizada. Total de produtos: {len(produtos)}")
    print(f"Arquivo gerado/atualizado: {ARQUIVO_JSON}")



def MercadoCarrefur():
    scraper = CarrefourScraper(base_url=CARREFOUR_BASE_URL, timeout=HTTP_TIMEOUT1)
    repository = JsonProductRepository(ARQUIVO_JSON1)
    service = ProductService(scrapers=[scraper], repository=repository)
    
    print("Iniciando coleta no catálogo online Carrefur...")
    produtos = service.coletar(CONSULTAS)
    print(f"Coleta finalizada. Total de produtos: {len(produtos)}")
    print(f"Arquivo gerado/atualizado: {ARQUIVO_JSON1}")
    

def MercadoNagumo():
    scraper = NagumoScraper(base_url=NAGUMO_BASE_URL, timeout=HTTP_TIMEOUT2)
    repository = JsonProductRepository(ARQUIVO_JSON2)
    service = ProductService(scrapers=[scraper], repository=repository)

    print("Iniciando coleta no catálogo online Nagumo...")
    produtos = service.coletar(CONSULTAS)
    print(f"Coleta finalizada. Total de produtos: {len(produtos)}")
    print(f"Arquivo gerado/atualizado: {ARQUIVO_JSON2}")


def main():
    contina = True
    while contina:
        print("Escolha uma opção:")
        print("3 - Coletar produtos do catálogo online Nagumo")
        print("2 - Coletar produtos do catálogo online Carrefur")
        print("1 - Coletar produtos do catálogo online Coop")
        print("0 - Sair")
        opcao = input("Opção: ")

        if opcao == "1":
            MercadoCOOP()
        elif opcao == "2":
            MercadoCarrefur()
        elif opcao == "3":
            MercadoNagumo()
        elif opcao == "0":
            contina = False
            print("Saindo do programa...")
        else:
            print("Opção inválida. Tente novamente.")

if __name__ == "__main__":
    main()
