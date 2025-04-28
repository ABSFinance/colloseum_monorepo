# Vault Manager Repository

## Files to Create

### Source Files

```
src/
├── subscriber/
│   ├── index.ts
│   ├── ZmqSubscriber.ts
│   └── MessageHandler.ts
├── validator/
│   ├── index.ts
│   ├── Validator.ts
│   └── Constraints.ts
├── executor/
│   ├── index.ts
│   ├── Executor.ts
│   └── TransactionManager.ts
├── database/
│   ├── index.ts
│   ├── models.ts
│   └── operations.ts
├── clients/
│   ├── index.ts
│   ├── zmq/
│   │   ├── index.ts
│   │   ├── ZmqClient.ts
│   │   └── types.ts
│   ├── supabase/
│   │   ├── index.ts
│   │   ├── SupabaseClient.ts
│   │   └── types.ts
│   ├── solana/
│   │   ├── index.ts
│   │   ├── SolanaClient.ts
│   │   └── types.ts
│   └── voltr/
│       ├── index.ts
│       ├── VoltrClient.ts
│       └── types.ts
├── types/
│   ├── index.ts
│   ├── messages.ts
│   └── vault.ts
└── utils/
    ├── index.ts
    ├── logger.ts
    └── errorHandler.ts
```

### Test Files

```
tests/
├── subscriber.test.ts
├── validator.test.ts
├── executor.test.ts
├── database.test.ts
└── clients/
    ├── zmq.test.ts
    ├── supabase.test.ts
    ├── solana.test.ts
    └── voltr.test.ts
```

### Configuration Files

```
├── package.json
├── tsconfig.json
├── jest.config.js
└── README.md
```

### Documentation Files

```
docs/
├── vault_manager_architecture.md
└── vault_manager_repo.md
```

## File Descriptions

### Source Files

1. **Subscriber Module**

   - `ZmqSubscriber.ts`: ZMQ message subscriber implementation
   - `MessageHandler.ts`: Message processing and routing logic

2. **Validator Module**

   - `Validator.ts`: Validation logic implementation
   - `Constraints.ts`: Protocol constraints definitions

3. **Executor Module**

   - `Executor.ts`: Transaction execution logic
   - `TransactionManager.ts`: Transaction management and retry logic

4. **Database Module**

   - `models.ts`: Database models and types
   - `operations.ts`: Database operations implementation

5. **Clients Module**

   - ZMQ Client: `ZmqClient.ts` and `types.ts`
   - Supabase Client: `SupabaseClient.ts` and `types.ts`
   - Solana Client: `SolanaClient.ts` and `types.ts`
   - Voltr Client: `VoltrClient.ts` and `types.ts`

6. **Types Module**

   - `messages.ts`: ZMQ message type definitions
   - `vault.ts`: Vault related type definitions

7. **Utils Module**
   - `logger.ts`: Logging configuration
   - `errorHandler.ts`: Error handling utilities

### Test Files

- Unit tests for each module
- Integration tests for client interactions
- Test configurations and fixtures

### Configuration Files

- `package.json`: Project dependencies and scripts
- `tsconfig.json`: TypeScript configuration
- `jest.config.js`: Jest test configuration
- `README.md`: Project documentation

### Documentation Files

- `vault_manager_architecture.md`: System architecture documentation
- `vault_manager_repo.md`: Repository structure documentation

## Key Components

### 1. Subscriber Module

```typescript
// ZmqSubscriber.ts
interface ZmqMessage {
  topic: string;
  poolId: string;
  payload: ReallocationPayload;
}

class ZmqSubscriber {
  private socket: zmq.Socket;

  constructor(config: ZmqConfig) {
    this.socket = new zmq.Socket("sub");
    this.socket.connect(config.address);
  }

  subscribe(topic: string): void;
  onMessage(handler: (msg: ZmqMessage) => Promise<void>): void;
}
```

### 2. Validator Module

```typescript
// Validator.ts
interface ValidationResult {
  isValid: boolean;
  errors: ValidationError[];
  warnings: ValidationWarning[];
}

class Validator {
  validateReallocation(plan: ReallocationPlan): Promise<ValidationResult>;
  checkProtocolConstraints(plan: ReallocationPlan): Promise<boolean>;
  verifyLiquidity(plan: ReallocationPlan): Promise<boolean>;
  checkDuplicates(plan: ReallocationPlan): Promise<boolean>;
}
```

### 3. Executor Module

```typescript
// Executor.ts
interface TransactionResult {
  success: boolean;
  transactionId: string;
  error?: Error;
}

class Executor {
  executeReallocation(plan: ReallocationPlan): Promise<TransactionResult>;
  updateVaultState(poolId: string, state: VaultState): Promise<void>;
  retryTransaction(tx: Transaction): Promise<TransactionResult>;
}
```

### 4. Database Module

```typescript
// models.ts
interface VaultState {
  poolId: string;
  currentAllocation: Allocation;
  lastUpdated: Date;
  status: VaultStatus;
}

class Database {
  updateVaultState(state: VaultState): Promise<void>;
  getVaultState(poolId: string): Promise<VaultState>;
  logTransaction(tx: Transaction): Promise<void>;
}
```

### 5. Clients Module

#### ZMQ Client

```typescript
// clients/zmq/ZmqClient.ts
interface ZmqConfig {
  address: string;
  options?: zmq.SocketOptions;
}

class ZmqClient {
  private socket: zmq.Socket;

  constructor(config: ZmqConfig) {
    this.socket = new zmq.Socket("sub");
    this.socket.connect(config.address);
  }

  subscribe(topic: string): void;
  onMessage(handler: (msg: ZmqMessage) => Promise<void>): void;
  close(): Promise<void>;
}
```

#### Supabase Client

```typescript
// clients/supabase/SupabaseClient.ts
interface SupabaseConfig {
  url: string;
  key: string;
}

class SupabaseClient {
  private client: SupabaseClient;

  constructor(config: SupabaseConfig) {
    this.client = createClient(config.url, config.key);
  }

  updateVaultState(state: VaultState): Promise<void>;
  getVaultState(poolId: string): Promise<VaultState>;
  logTransaction(tx: Transaction): Promise<void>;
}
```

#### Solana Client

```typescript
// clients/solana/SolanaClient.ts
interface SolanaConfig {
  rpcUrl: string;
  wsUrl?: string;
  commitment?: Commitment;
  timeout?: number;
}

class SolanaClient {
  private connection: Connection;
  private wallet: Wallet;

  constructor(config: SolanaConfig, wallet: Wallet) {
    this.connection = new Connection(config.rpcUrl, {
      commitment: config.commitment || "confirmed",
      wsEndpoint: config.wsUrl,
      timeout: config.timeout || 30000,
    });
    this.wallet = wallet;
  }

  async sendTransaction(transaction: Transaction): Promise<string> {
    const signature = await this.connection.sendTransaction(
      transaction,
      [this.wallet.payer],
      { skipPreflight: false }
    );
    return signature;
  }

  async confirmTransaction(signature: string): Promise<boolean> {
    const confirmation = await this.connection.confirmTransaction(signature);
    return confirmation.value.err === null;
  }

  async getBalance(publicKey: PublicKey): Promise<number> {
    const balance = await this.connection.getBalance(publicKey);
    return balance;
  }

  async getTokenAccounts(owner: PublicKey): Promise<TokenAccount[]> {
    const accounts = await this.connection.getParsedTokenAccountsByOwner(
      owner,
      {
        programId: TOKEN_PROGRAM_ID,
      }
    );
    return accounts.value;
  }
}
```

#### Voltr Client

```typescript
// clients/voltr/VoltrClient.ts
interface VoltrConfig {
  apiKey: string;
  baseUrl: string;
}

class VoltrClient {
  private client: VoltrSDK;

  constructor(config: VoltrConfig) {
    this.client = new VoltrSDK(config);
  }

  executeTrade(trade: Trade): Promise<TradeResult>;
  getMarketData(poolId: string): Promise<MarketData>;
}
```

## Dependencies

```json
{
  "dependencies": {
    "zmq": "^0.0.0",
    "@solana/web3.js": "^0.0.0",
    "typeorm": "^0.0.0",
    "winston": "^0.0.0"
  },
  "devDependencies": {
    "@types/node": "^0.0.0",
    "@types/jest": "^0.0.0",
    "typescript": "^0.0.0",
    "jest": "^0.0.0",
    "ts-jest": "^0.0.0"
  }
}
```

## Development Setup

1. Clone the repository
2. Install dependencies:
   ```bash
   npm install
   ```
3. Set up environment variables:
   ```bash
   cp .env.example .env
   # Edit .env with your configuration
   ```
4. Run tests:
   ```bash
   npm test
   ```

## Testing

- Jest for unit and integration tests
- Mock Solana RPC for testing
- Database test fixtures
- Type checking with TypeScript

## Build and Run

1. Build the project:
   ```bash
   npm run build
   ```
2. Run in development:
   ```bash
   npm run dev
   ```
3. Run in production:
   ```bash
   npm start
   ```

## Docker Deployment

1. Build Docker image:
   ```bash
   docker build -t vault-manager .
   ```
2. Run container:
   ```bash
   docker run -d --env-file .env vault-manager
   ```

## Monitoring

- Winston logger configuration
- Prometheus metrics
- Error tracking with Sentry
- Transaction status monitoring

## Contributing

1. Fork the repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create pull request

## License

[License Type] - See LICENSE file for details
