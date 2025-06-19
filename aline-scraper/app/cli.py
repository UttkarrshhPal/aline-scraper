import click
from .config import Config

@click.group()
def cli():
    """Aline Scraper CLI"""
    pass

@cli.command()
def show_config():
    """Show current configuration."""
    config = Config()
    click.echo(f"Database URL: {config.database_url}")
    click.echo(f"Redis URL: {config.redis_url}")
    click.echo(f"Request Delay: {config.request_delay}")
    click.echo(f"Max Retries: {config.max_retries}")
    click.echo(f"Timeout Seconds: {config.timeout_seconds}")
    click.echo(f"Max Concurrent Jobs: {config.max_concurrent_jobs}")
    click.echo(f"Chunk Size: {config.chunk_size}")
    click.echo(f"Chunk Overlap: {config.chunk_overlap}")
    click.echo(f"Log Level: {config.log_level}")
    click.echo(f"Log Format: {config.log_format}")

@cli.command()
@click.argument('source')
def scrape(source):
    """Run a scrape job for the given source (placeholder)."""
    click.echo(f"Scraping source: {source} (not implemented)")

if __name__ == '__main__':
    cli() 