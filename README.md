# 📘 Documentação Técnica — Microserviço `account`

### 🧩 Finalidade

O `account` é o serviço central do Ledger. Ele mantém a **fonte de verdade contábil** de todas as contas (fornecedores, lojistas ou qualquer entidade), armazenando transações com integridade contábil, garantindo rastreabilidade, consistência e comunicação com o serviço `balance` para manter o saldo atualizado.

---

## 🔁 Responsabilidades

- Gerenciar contas e seus status.
- Armazenar transações associadas a contas.
- Garantir idempotência de transações via ULID.
- Disparar reconciliação no `balance` ao registrar uma nova transação.
- Oferecer APIs para gravação e leitura de transações.

---

## 🗃️ Estrutura de Dados

### Modelo: `Account`

| Campo              | Tipo                                    | Descrição                                                                   | Exemplo             |
|--------------------|-----------------------------------------|--------------------------------------------------------------------------------------|--------------------------|
| `id`               | `string (ULID)`                         | Identificador único da conta.                                                        | `"01HYXY..."`             |
| `tenant_id`        | `int`                                   | Identificador do tenant responsável pelo evento.                                 | `1`             |
| `owner_id`         | `string`                                | Identificador externo do dono da conta (ex: lojista, fornecedor).                   | `"lojista-ABC"`          |
| `status`           | `"ACTIVE"` / `"SUSPENDED"` / `"CLOSED"` | Estado da conta.                                                                     | `"SUSPENDED"`            |
| `suspension_reason`| `string (condicional)`                  | Obrigatório se o status for `"SUSPENDED"`. Indica o motivo da suspensão. | `"inadimplência"`        |
| `created_at`       | `datetime`                              | Data de criação da conta.                                                            | `"2025-06-01T10:00:00Z"` |

### Regras:
- Status `CLOSED` é final — não pode ser revertido ou modificado.
- Ao suspender, o campo `suspension_reason` é obrigatório.

---

### Modelo: `TransactionEntry`

| Campo             | Tipo                           | Descrição                                         | Exemplo                 |
|-------------------|--------------------------------|---------------------------------------------------|-------------------------|
| `id`              | `string (ULID)`                | Identificador único e ordenável da transação.    | `"01HYXY..."`           |
| `tenant_id`       | `int`                          | Identificador do tenant responsável pelo evento. | `1`                     |
| `account_id`      | `str`                          | Conta de destino da transação.                    | `"01HYXY..."`           |
| `timestamp`       | `datetime`                     | Momento da transação (UTC).                       | `"2025-06-11T14:30:00Z"`|
| `amount`          | `float`                        | Valor absoluto da transação.                      | `100.00`                |
| `type`            | `"DEBIT"` / `"CREDIT"`         | Direção da transação.                             | `"CREDIT"`              |
| `currency`        | `string`                       | Moeda da transação (ex: `"BRL"`).                 | `"BRL"`                 |
| `product`         | `string`                       | Produto/serviço que gerou a transação.            | `"VOUCHER"`             |
| `reference`       | `string`                       | Identificador legível e obrigatório da transação. | `"Pedido #8823"`        |
| `metadata`        | `dict[string, Any] (opcional)` | Informações contextuais variáveis.                | `{"parcelas": 12}`      |
| `balance_snapshot`| `float (calculado)`            | Saldo da conta imediatamente após esta transação. | `190.00`                |

---

## 📤 Endpoints

#### `POST /accounts`
Criação de conta.

#### `PATCH /accounts/{account_id}/status`
Atualização de status da conta.  
Regras:
- Não é possível modificar uma conta `CLOSED`.
- `suspension_reason` obrigatório quando status for `SUSPENDED`.

#### `GET /accounts/{account_id}`
Consulta de conta.

#### `POST /accounts/{account_id}/transactions`
Inclusão de transação (usado pelo `transaction-worker`).

#### `GET /accounts/{account_id}/transactions`
Consulta de transações por conta (usado pelo `statement`).
Regras:
- Paginação obrigatória.
- Filtro obrigatório por timestamp inicial e final da transação.
- Filtro por product, que caso omitido, retorno todos os produtos.

---

## 🔁 Requisição ao `balance`

Ao registrar uma transação, o `account` deve acionar microsserviço 
`balance` para reconciliação.

---

## 🧠 Regras de Transação

- Cada transação é única por `id`.
- Transações com ULID repetido:
  - Devem ser registradas em uma base separada (`rejected_transactions`).
  - Logar motivo e manter rastreabilidade.
- Transações só são aceitas para contas `ACTIVE`.

---

## 📊 Observabilidade

### Logs:
- `INFO`: criação de conta, inserção de transação.
- `WARN`: status inválido, duplicidade de transação.
- `ERROR`: erro no banco, erro na reconciliação, falha interna.

### Métricas:
- `account_transactions_total`
- `account_status_changes_total`
- `account_rejected_transactions_total`
- `account_reconciliation_errors_total`

---

## ✅ Cenários de Teste

1. ✅ Criação de conta
2. ✅ Suspensão com motivo válido
3. ❌ Suspensão sem motivo
4. ❌ Tentativa de alterar conta `CLOSED`
5. ✅ Inserção de transação válida
6. ✅ Acionamento do `balance` após transação
7. ❌ Inserção duplicada (verificação em `rejected_transactions`)
8. ✅ Consulta de extrato com paginação