# Freqtrade official image + the few extra libraries the research scripts use.
FROM freqtradeorg/freqtrade:stable
USER root
RUN pip install --no-cache-dir matplotlib pytest
USER ftuser
