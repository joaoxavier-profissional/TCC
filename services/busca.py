"""Regras de filtragem e ordenação de eventos indexados."""
from services.video import segundos


def filtrar_eventos(eventos, classe="Todas", video="Todos", inicio=None, fim=None,
                   ordenacao="Horário (crescente)"):
    """Filtra eventos por interseção com o intervalo solicitado.

    Eventos têm formato (nome_video, classe, inicio, fim).
    inicio/fim são segundos desde o começo de cada gravação.
    """
    if inicio is not None and fim is not None and inicio > fim:
        raise ValueError("O horário inicial não pode ser maior que o final.")

    encontrados = []
    for evento in eventos:
        nome, tipo, t_inicio, t_fim = evento
        if classe != "Todas" and tipo != classe:
            continue
        if video != "Todos" and nome != video:
            continue
        try:
            a, b = segundos(t_inicio), segundos(t_fim)
        except (TypeError, ValueError):
            continue
        # Inclui eventos que cruzam, mesmo parcialmente, a janela pesquisada.
        if inicio is not None and b < inicio:
            continue
        if fim is not None and a > fim:
            continue
        encontrados.append(evento)

    if ordenacao == "Horário (decrescente)":
        return sorted(encontrados, key=lambda e: (segundos(e[2]), e[0]), reverse=True)
    if ordenacao == "Classe (A–Z)":
        return sorted(encontrados, key=lambda e: (e[1].casefold(), e[0], segundos(e[2])))
    if ordenacao == "Gravação (A–Z)":
        return sorted(encontrados, key=lambda e: (e[0].casefold(), segundos(e[2])))
    return sorted(encontrados, key=lambda e: (segundos(e[2]), e[0]))
