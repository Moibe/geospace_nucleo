module.exports = {
  apps: [
    {
      name: "geospace-nucleo",
      script: "venv/bin/uvicorn",
      args: "api.app:app --host 0.0.0.0 --port 8001",
      cwd: "/home/deploy/geospace_nucleo",  // Se sobreescribe con WORK_DIR en prod
      interpreter: "none",
      env: {
        ENVIRONMENT: "production",
      },
      // Reiniciar si consume más de 512MB
      max_memory_restart: "512M",
      // Logs
      error_file: "logs/err.log",
      out_file: "logs/out.log",
      merge_logs: true,
      log_date_format: "YYYY-MM-DD HH:mm:ss",
    },
  ],
};
