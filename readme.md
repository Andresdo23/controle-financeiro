#  Controle Financeiro Pessoal

Projeto  **Controle Financeiro Pessoal** desenvolvido em **Python** com **Streamlit**, aplicando conceitos de **Programação Funcional**.  

Este projeto foi desenvolvido para contemplar os requisitos de:  
- Lambda  
- Closure  
- Função de alta ordem  
- List comprehension  
- CRUD de transações financeiras  

---

## Objetivo

Permitir que um usuário registre, edite, exclua e visualize suas transações financeiras pessoais (receitas e despesas), com filtros, ordenação e métricas de saldo, exportando os dados em CSV ou JSON.

---

##  Papéis e Responsabilidades (6 integrantes)

| Integrante | Papel | Responsabilidades |
|------------|-------|-----------------|
| André Silva | Documentação | Elaborar requisitos, casos de teste e documentação do projeto |
| Henrique Correia | Backend | Implementação das funções de CRUD e lógica do sistema |
| André Silva | Backend | Persistência de dados, geração de IDs e tratamento de erros |
| Natan Aguine | Frontend | Interface Streamlit: formulários, tabela, filtros e métricas |
| Thayná Stephanie | Testes | Casos de teste e validação de funcionalidades |
| Integrante 6 | Integração | Deploy e execução da aplicação, exportação de dados |

---

##  Requisitos Funcionais

1. Adicionar transação (tipo, valor, descrição, categoria)  
2. Editar transação (descrição, categoria e valor)  
3. Excluir transação pelo ID  
4. Consultar todas as transações registradas  
5. Filtrar transações por tipo e categoria  
6. Ordenar transações por data, valor, ID, categoria, descrição ou tipo  
7. Calcular e exibir métricas de saldo, total de receitas e despesas  
8. Exportar dados em CSV ou JSON  
 

---

##  Requisitos Não Funcionais

- Persistência de dados em arquivo JSON  
- Robustez e tratamento de erros  
- Performance rápida para até 1000 transações  
- Interface amigável e responsiva  
- Compatível com Python 3.10+ e Streamlit 1.0+  

---

##  Tecnologias Utilizadas

- **Python 3.10+**  
- **Streamlit**  
- **Pandas**  
- **JSON**
- **VsCode** 

---

##  Programação Funcional no Código

| Conceito | Local no Código | Observação |
|-----------|----------------|------------|
| Lambda | `agora = lambda: datetime.now().strftime("%H:%M:%S %d/%m/%Y")` | Gera timestamp |
| Closure | `gerar_id(transacoes)` | Mantém controle do ID das transações |
| Função de Alta Ordem | `selecionar(transacoes, criterio)` | Recebe função como parâmetro para filtrar dados |
| List Comprehension | `selecionar` e `formatar_tabela` | Criação de listas filtradas ou para exibição |

---

##  Como Rodar o Projeto

1. Clone o repositório:

git clone https://github.com/Andresdo23/controle-financeiro.git
cd controle-financeiro

2. Instale as dependências:

pip install streamlit pandas

3. Execute a aplicação:

streamlit run app.py
