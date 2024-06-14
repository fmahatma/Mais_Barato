import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
from bs4 import BeautifulSoup
import pandas as pd

# Function to load URLs from a file
def load_urls(filename):
    urls = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                if line.strip():
                    name, url = line.strip().split(',')
                    urls[name] = url
    except FileNotFoundError:
        print(f"Error: The file '{filename}' was not found.")
    except Exception as e:
        print(f"Error reading '{filename}': {e}")
    return urls

# Function to scrape data from a supermarket
def scrape_supermarket(url):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/90.0.4430.93 Safari/537.36"
    }
    produtos = []

    # Set up retry logic
    retry_strategy = Retry(
        total=3,
        backoff_factor=1,
        status_forcelist=[429, 500, 502, 503, 504],
        allowed_methods=["HEAD", "GET", "OPTIONS"]
    )
    adapter = HTTPAdapter(max_retries=retry_strategy)
    http = requests.Session()
    http.mount("https://", adapter)
    http.mount("http://", adapter)

    try:
        response = http.get(url, headers=headers)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        for produto in soup.select('.product-card'):
            nome = produto.select_one('.product-card__title').get_text(strip=True)
            marca = produto.select_one('.product-card__brand').get_text(strip=True)
            peso = produto.select_one('.product-card__weight').get_text(strip=True)
            preco = produto.select_one('.product-card__price').get_text(strip=True)
            if "5kg" in peso.lower() and "branco" in nome.lower():
                produtos.append({
                    "Nome do Produto": nome,
                    "Marca": marca,
                    "Peso": peso,
                    "Preço": preco,
                    "Fonte": url
                })
    except requests.exceptions.RequestException as e:
        print(f"Error fetching data from {url}: {e}")
    return produtos

def main():
    urls = load_urls('urls.txt')
    all_products = []
    for name, url in urls.items():
        products = scrape_supermarket(url)
        all_products.extend(products)
    if all_products:
        df = pd.DataFrame(all_products)
        print(df)
    else:
        print("No products found.")

if __name__ == '__main__':
    main()
