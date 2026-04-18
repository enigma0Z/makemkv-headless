export type LogLevel = "ERROR" | "WARNING" | "INFO" | "DEBUG"

export type Config = {
  config_file: string;
  destination: string;
  source: string;
  tmdb_token: string;
  makemkvcon_path: string;
  log_level: LogLevel;
  log_file: string;
  temp_prefix: string;
  frontend: string;
  listen_port: string;
  cors_origins: string[];
  ui_path: string;
}