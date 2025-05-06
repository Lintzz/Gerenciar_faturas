# Gerenciador de Faturas

## Descrição do Projeto
Este é um sistema de gerenciamento de faturas desenvolvido em Python, especialmente otimizado para faturas do Nubank. O sistema permite importar, visualizar, categorizar e analisar despesas através de uma interface gráfica intuitiva.

## Tecnologias Utilizadas

### Principais Bibliotecas
- **tkinter/customtkinter**: Interface gráfica do usuário
- **PyPDF2**: Processamento de arquivos PDF
- **matplotlib**: Geração de gráficos e visualizações
- **sqlite3**: Banco de dados local
- **PIL (Python Imaging Library)**: Manipulação de imagens
- **tkcalendar**: Componente de calendário para seleção de datas

## Estrutura do Projeto

### Arquivos Principais
- `app.py`: Aplicação principal com a interface gráfica
- `Tratamento_pdf.py`: Processamento e extração de dados de PDFs
- `BancoDados.py`: Gerenciamento do banco de dados SQLite
- `config.py`: Configurações globais do sistema
- `AppPOO.py`: Versão orientada a objetos da aplicação

### Funcionalidades Principais

#### 1. Processamento de PDF
- Extração automática de dados de faturas
- Normalização de descrições de transações
- Categorização automática de despesas

#### 2. Gerenciamento de Dados
- Armazenamento em banco de dados SQLite
- Organização por ano e mês
- Sistema de categorização personalizado

#### 3. Visualização
- Interface gráfica moderna e intuitiva
- Gráficos de análise de despesas
- Filtros e pesquisas avançadas

#### 4. Recursos Adicionais
- Calendário integrado
- Sistema de edição de transações
- Exportação de dados
- Visualização em diferentes formatos

## Categorias de Despesas
O sistema inclui as seguintes categorias predefinidas:
- Assinaturas
- Compras
- Transporte
- Saúde
- Alimentação
- Celular
- Diversos

## Como Usar

### Requisitos do Sistema
- Python 3.x
- Bibliotecas listadas em `requirements.txt`

### Instalação
1. Clone o repositório
2. Instale as dependências:
```bash
pip install -r requirements.txt
```

### Executando o Programa
1. Execute o arquivo principal:
```bash
python app.py
```

### Fluxo de Trabalho Básico
1. Importe uma fatura PDF do Nubank
2. O sistema processará automaticamente o arquivo
3. Visualize e edite as transações conforme necessário
4. Use as ferramentas de análise para gerar relatórios

## Funcionalidades Detalhadas

### Processamento de PDF
- Extração automática de dados
- Padronização de descrições
- Categorização automática
- Limpeza e formatação de dados

### Interface do Usuário
- Treeview para visualização de transações
- Calendário para seleção de datas
- Gráficos interativos
- Filtros e pesquisa

### Banco de Dados
- Estrutura organizada por ano/mês
- Backup automático
- Sistema de consultas otimizado

### Análise de Dados
- Gráficos de distribuição de gastos
- Análise por categoria
- Comparativos mensais
- Exportação de relatórios

## Manutenção e Suporte

### Arquivos de Configuração
- Configurações globais em `config.py`
- Diretório de armazenamento configurável
- Personalização de categorias

### Backup
- Os dados são armazenados em arquivos SQLite
- Recomenda-se backup regular do diretório de dados

## Contribuição
Para contribuir com o projeto:
1. Fork o repositório
2. Crie uma branch para sua feature
3. Faça commit das alterações
4. Push para a branch
5. Crie um Pull Request

## Resolução de Problemas
- Verifique as permissões de arquivo
- Confirme se todas as dependências estão instaladas
- Verifique a compatibilidade do Python

## Notas de Versão
- Sistema em desenvolvimento ativo
- Atualizações regulares de funcionalidades
- Correções de bugs conforme necessário

## Licença
Este projeto está sob licença. Consulte o arquivo LICENSE para mais detalhes. 