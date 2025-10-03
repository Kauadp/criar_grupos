rm(list = ls())

library(tidyverse)
library(jsonlite)

dados <- read.csv("dados/stand_es.csv")

dados <- dados[c(1:181, 213,215),1:34]

dados <- dados |> 
  mutate(
    nome_grupo = paste(str_to_title(Expositor..N.Fantasia), "-", "Exagerado")
  )

dados$RECORRENTE <- dados$RECORRENTE |> 
  str_trim() |> 
  str_to_upper()

recorrentes <- c(
  "NOVO" = "NOVO",
  "RECORRENTE" = "RECORRENTE",
  "NOVO/ RECORRENTE" = "NOVO",
  "NOVO/RECORRENTE" = "NOVO",
  "RECORRENTE/NOVO" = "NOVO",
  "RECORRENTE/RESGATE" = "RECORRENTE"
)

dados <- dados |>
  mutate(RECORRENTE = recode(RECORRENTE, !!!recorrentes))

dados$vendido <- str_to_upper(dados$vendido)
dados$CONTRATO.ASSINADO. <- str_to_upper(dados$CONTRATO.ASSINADO.)

dados_grupo <- dados |> 
  filter(RECORRENTE == "NOVO" & vendido == "SIM" & CONTRATO.ASSINADO. == "ASSINADO")

dados_grupo <- dados_grupo |> 
  select(
    nome_grupo,
    TELEFONE
  )
  
dados_grupo$TELEFONE <- str_trim(dados_grupo$TELEFONE)

padronizar_telefone_br <- function(vetor_telefones) {
  telefones_limpos <- str_replace_all(vetor_telefones, "[^0-9]", "")
  telefones_extraidos <- str_extract(telefones_limpos, "(\\d{10,11})")
  condicao_valida <- !is.na(telefones_extraidos) & str_length(telefones_extraidos) %in% c(10, 11)
  telefones_padronizados <- rep(NA_character_, length(vetor_telefones))
  telefones_padronizados[condicao_valida] <- paste0("55", telefones_extraidos[condicao_valida])
  return(telefones_padronizados)
}

dados_grupo$numero_variavel <- padronizar_telefone_br(dados_grupo$TELEFONE)
dados_grupo <- dados_grupo |> 
  select(!TELEFONE)

jsonlite::write_json(toJSON(dados_grupo), path = "dados/dados_grupo.JSON")
