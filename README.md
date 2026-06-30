# RPA - Baixa Interna Automática Correios

Sistema de Automação de Processos Robóticos (RPA) desenvolvido em Python para realizar a baixa interna automática de objetos nos Correios. O projeto utiliza uma arquitetura híbrida com **Supabase** (banco em nuvem) para centralização dos dados e **SQLite** (banco local) para controle de fila, resiliência offline e cache.

## 🚀 Funcionalidades
*   **Automação de Baixas:** Processamento automatizado de status e atualizações no sistema dos Correios.
*   **Arquitetura Híbrida de Dados:** Sincronização inteligente entre o banco local (SQLite) e a nuvem (Supabase).
*   **Resiliência e Tolerância a Falhas:** Mecanismo de retry e armazenamento local para evitar perda de dados em caso de instabilidade na rede ou no portal dos Correios.
*   **Logs Estruturados:** Rastreabilidade completa de cada etapa do processo e auditoria de falhas.

## 🛠️ Tecnologias Utilizadas
*   **Python 3.x**
*   **Supabase Client:** Integração e persistência de dados em nuvem.
*   **SQLite3:** Banco local para gerenciamento de estado e fila de execução.
*   **Logging:** Monitoramento nativo da saúde do robô.

## 📋 Pré-requisitos
Antes de começar, certifique-se de ter instalado:
*   Python 3.10 ou superior
*   Uma conta ativa no [Supabase](https://supabase.com/) com as credenciais do seu projeto.

## 🔧 Configuração e Instalação

1. **Clone o repositório:**
   ```bash
   git clone [https://github.com/silasagfcharlesmiller-commits/rpa-baixa-correios.git](https://github.com/silasagfcharlesmiller-commits/rpa-baixa-correios.git)
   cd rpa-baixa-correios
