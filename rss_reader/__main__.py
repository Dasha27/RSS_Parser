import argparse
import sys
from rss_reader.rss_parser import RSSParser
from rss_reader.logger import start_logging
from pathlib import Path
from rss_reader import VERSION


def main():
    parser = argparse.ArgumentParser(prog='rss_reader.py ', description='Pure Python command-line RSS reader.',
                                     epilog='Enjoy the program! :)')
    parser.add_argument('source', nargs='?', type=str, help='RSS URL')
    parser.add_argument('--version', action='version', version=f'%(prog)s {VERSION}', help='Print version info')
    parser.add_argument('--json', action='store_true', help='Print result as JSON in stdout')
    parser.add_argument('--verbose', action='store_false', help='Output verbose status messages')
    parser.add_argument('--limit', type=int, help='Limit news topics if this parameter provided')
    parser.add_argument('--date', type=str,
                        help='Print news from the specified day. Required date format - %Y%m%d')
    parser.add_argument('--to_pdf', type=Path, help='Convert news to PDF and save to entered file')
    parser.add_argument('--to_html', type=Path, help='Convert news to HTML and save to entered file')

    args = parser.parse_args()

    url = args.source
    limit = args.limit
    json = args.json
    date = args.date
    html_path = args.to_html
    pdf_path = args.to_pdf

    parser = RSSParser(url, limit, date, html_path, pdf_path)

    log = start_logging()
    log.disabled = args.verbose

    log.info('The RSS Parser started working')
    if url:
        log.info('The url was received from CLI')
        parser.open_url()
        log.info('The parser opened the url')
        if html_path:
            log.info('Converting to HTML started')
            parser.convert_news_to_html()
            log.info('Converting to HTML finished')
        if pdf_path:
            log.info('Converting to PDF started')
            parser.convert_news_to_pdf()
            log.info('Converting to PDF finished')
        if date and json:
            log.info('Getting info from cache from the specified resource started')
            log.info('Converting to JSON started')
            parser.get_news_from_cache_in_json()
            log.info('Converting to JSON finished')
            log.info('Getting info from cache from the specified resource finished')
        elif json:
            log.info('Converting to JSON started')
            parser.save_news_to_dictionary()
            parser.convert_news_into_json()
            log.info('Converting to JSON finished')
            log.info('Saving to cache started')
            parser.save_news_to_file()
            log.info('Saving to cache finished')
        elif date:
            log.info('Getting info from cache from the specified resource started')
            parser.get_news_from_cache()
            log.info('Getting info from cache from the specified resource finished')
        else:
            log.info('Printing to stdout started')
            parser.print_news_to_stdout()
            log.info('Printing to stdout finished')
            log.info('Saving to cache started')
            parser.save_news_to_dictionary()
            parser.save_news_to_file()
            log.info('Saving to cache finished')
    else:
        if date and json:
            log.info('Getting info from cache started')
            log.info('Converting to JSON started')
            parser.get_news_from_cache_in_json()
            log.info('Converting to JSON finished')
            log.info('Getting info from cache finished')
        elif date:
            log.info('Getting info from cache started')
            parser.get_news_from_cache()
            log.info('Getting info from cache finished')
        else:
            log.warning('The url was not entered')
            try:
                raise ValueError('RSS Parser stopped: missing source argument')
            except ValueError as exc:
                sys.exit(f'Please, enter an url - {exc}')
    log.info('The RSS Parser finished working')


if __name__ == '__main__':
    sys.exit(main())
