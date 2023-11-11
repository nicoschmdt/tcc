import json

import matplotlib.pyplot as plt


def create_graph(name: str):
    read_skmob(name)


def get_info(columns):
    values = {key: 0 for key in [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]}
    for _, risk in columns['data']:
        try:
            values[risk] += 1
        except KeyError:
            values[risk] = 1

    return zip(*sorted(values.items()))


def read_skmob(names: list[str], attack: str, markers, title: str):
    for name in names:
        with open(f'{name}-{attack}.json', 'r') as f:
            data = json.load(f)

        _, results, _, _ = data
        results = json.loads(results)
        x, y = get_info(results)
        plt.plot(x, y, marker=markers[name], label=name)

    # Gráfico
    plt.xlabel("Risco", fontsize=16, weight='bold')
    plt.ylabel("Quantidade de Trajetórias", fontsize=16, weight='bold')
    plt.xticks(fontsize=15, weight='bold')
    plt.yticks(fontsize=15, weight='bold')
    plt.xticks([0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1])
    plt.legend(fontsize=14, loc='upper left').set_title("Legenda")
    plt.title(title, fontsize=17, weight='bold')

    # plt.show()
    plt.savefig(f'{attack}', bbox_inches='tight')


#
# plt.savefig(file_name, bbox_inches='tight')
# plt.show()


if __name__ == '__main__':
    # depois adicionar 'tu' e 'tu-TKY'
    # executar todos deixa a Legenda estranha
    markers = {'nyc': 'o', 'tky': 's', 'zhang': '^', 'zhang-TKY': 'v', 'naghizade': '*',
               'naghizade-TKY': 'D', 'tu': '<', 'tu-TKY': '>'}
    names = ['nyc', 'tky', 'zhang', 'zhang-TKY', 'naghizade', 'naghizade-TKY', 'tu', 'tu-TKY']
    # read_skmob(names, 'location', markers, title='Ataque de Lugar')
    # read_skmob(names, 'sequence', markers, title='Ataque de Sequência de Lugar')
    # read_skmob(names, 'time', markers, title='Ataque de Horário de Lugar')
    # read_skmob(names, 'unique', markers, title='Ataque de Lugar Único')
    # read_skmob(names, 'frequency', markers, title='Ataque de Frequência')
    read_skmob(names, 'probability', markers, title='Ataque de Probabilidade')
    # read_skmob(names, 'proportion', markers, title='Ataque de Proporção')
    # read_skmob(names, 'homework', markers, title='Ataque de Casa-Trabalho')
