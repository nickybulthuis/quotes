# Quotes
[![Build and Test](https://github.com/nbult/quotes/actions/workflows/build-and-test.yml/badge.svg)](https://github.com/nbult/quotes/actions/workflows/build-and-test.yml)

Once you start investing, it is desirable to keep track of your progress. It is logical; you have embarked on a new
aspect of your finances and want to keep an eye on it.

However, getting stock quotes for funds that are not available on Yahoo Finance or one of the more popular stock
information websites is not easy. Sometimes the only source of information is the fund manager's website and even then
the information provided is often not readily available nor in a structured format.

The purpose of this project is to provide stock quotes for specific funds, by accessing the fund manager's website, by
filling in forms, or by using other APIs to request them. The stock prices are then converted into a structured format
for use in [Portfolio Performance](https://www.portfolio-performance.info/), Excel or equivalent.

It's basically trying to automate what you could do by hand.

## Supported websites

* [Meesman](https://meesman.nl)
* [Brand New Day](https://brandnewday.nl)

You can either use the public endpoint or host the project yourself in Docker (see below). 

## Portfolio Performance

[Portfolio Performance](https://www.portfolio-performance.info/) is an open-source tool to track your investments. It
allows you to automatically download stock prices or quotes for your securities.

#### Meesman

Use the following settings to download Historical Quotes for *Meesman* funds. For Latest Quote, use the (same as
historical quotes) option.
| Setting | Value |
| ----------- | ----------- |
| Provider | JSON Feed |
| URL | https://quotes.totalechaos.nl/meesman/aandelen-wereldwijd-totaal |
| Path to Date | $.[*].Date |
| Path to Close | $.[*].Close |

You can replace **aandelen-wereldwijd-totaal** with any of the other available fund names.

#### Brand New Day

Use the following settings to download Historical Quotes for *Brand New Day* funds. For Latest Quote, use the (same as
historical quotes) option.
| Setting | Value |
| ----------- | ----------- |
| Provider | JSON Feed |
| URL | https://quotes.totalechaos.nl/brandnewday/bnd-wereld-indexfonds-c-unhedged?page={PAGE} |
| Path to Date | $.[*].Date |
| Path to Close | $.[*].Close |

You can replace **bnd-wereld-indexfonds-c-unhedged** with any of the other available fund names.

## Excel

Excel has the ability to download json data from the web and transform it in to a table. To use the API in excel, follow
the following steps.

1. Navigate to the Data tab.
2. Click 'From Web' and use URL: https://quotes.totalechaos.nl/meesman/aandelen-wereldwijd-totaal.
3. Excel will now load the JSON data and you should see a list of 'Records'.
4. Click 'To Table' on the 'Transform' tab.
5. Click the 'Expand Column' icon on the Column 1 header.
6. Select the columns you wish (Date, Close) and click Ok.
7. For each column, click the type icon in the header and select the appropriate type (Date/Time and Decimal).
8. Click 'Close and Load' and the should now see the stock prices for your fund.

## Docker

This project is very easy to install and deploy in a Docker container.

By default, the Docker will expose port 80. Simply use the Dockerfile to
build the image.

```sh
git clone git@github.com:nbult/quotes.git
cd quotes
docker build --tag quotes .
```

This will create the quotes image and pull in the necessary dependencies.

Once done, run the Docker image and map the port to whatever you wish on
your host. In this example, we simply map port 80 of the host to
port 80 of the Docker container:

```sh
docker run -d -p 80:80 --restart=always --name=quotes quotes
```

The API documentation will be available on http://127.0.0.1/

## Disclaimer

This API is not affiliated, associated, authorized, endorsed by or in any way officially associated with the said
websites, or any of its subsidiaries or affiliates. The official websites can be found at their respective links.

All names and related names, brands, emblems and images are registered trademarks of theirs respective owners.
