import * as fs from "fs";
import {
  AddressLookupTableAccount,
  Connection,
  Keypair,
  PublicKey,
  SYSVAR_INSTRUCTIONS_PUBKEY,
  TransactionInstruction,
} from "@solana/web3.js";
import { getAccount, TOKEN_PROGRAM_ID } from "@solana/spl-token";
import { sendAndConfirmOptimisedTx, setupTokenAccount } from "../../utils/helper";
import { BN } from "@coral-xyz/anchor";
import {
  LENDING_ADAPTOR_PROGRAM_ID,
  SEEDS,
  VoltrClient,
} from "@voltr/vault-sdk";
import {
  managerFilePath,
  marginfiAccount,
  heliusRpcUrl,
  vaultAddress,
  withdrawAssetAmountPerStrategy,
  assetMintAddress,
  assetTokenProgram,
  outputMintAddress,
  lookupTableAddress,
  useLookupTable,
  outputTokenProgram,
} from "./utils/variables";
import { PROTOCOL_CONSTANTS } from "./constants";
import { setupJupiterSwapForWithdrawStrategy } from "./utils/setup-jupiter-swap";

const payerKpFile = fs.readFileSync(managerFilePath, "utf-8");
const payerKpData = JSON.parse(payerKpFile);
const payerSecret = Uint8Array.from(payerKpData);
const payerKp = Keypair.fromSecretKey(payerSecret);
const payer = payerKp.publicKey;

const vaultOutputMint = new PublicKey(outputMintAddress);
const vaultOutputTokenProgram = new PublicKey(outputTokenProgram);


/**
 * Parameters for withdrawing from a Solend strategy
 */
export interface SolendWithdrawParams {
  /** The Voltr client */ 
  vc: VoltrClient,
  /** The connection */
  connection: Connection,
  /** The vault address */
  vault: PublicKey,
  /** The payer keypair */
  payerKp: Keypair,
  /** The asset token program */
  vaultAssetTokenProgram: PublicKey,
  /** The output mint */
  vaultAssetMint: PublicKey,
  /** The amount to withdraw */
  withdrawAmount: BN;
  /** The program ID of the Solend protocol */
  protocolProgram: PublicKey;
  /** The token account of the counterparty */
  counterPartyTa: PublicKey;
  /** The lending market account */
  lendingMarket: PublicKey;
  /** The reserve account */
  reserve: PublicKey;
  /** The collateral mint account */
  collateralMint: PublicKey;
  /** The Pyth oracle account */
  pythOracle: PublicKey;
  /** The Switchboard oracle account */
  switchboardOracle: PublicKey;
  /** Optional lookup table addresses */
  lookupTableAddresses?: string[];
}

/**
 * Parameters for withdrawing from a Marginfi strategy
 */
export interface MarginfiWithdrawParams {
  /** The Voltr client */ 
  vc: VoltrClient,
  /** The connection */
  connection: Connection,
  /** The vault address */
  vault: PublicKey,
  /** The payer keypair */
  payerKp: Keypair,
  /** The asset token program */
  vaultAssetTokenProgram: PublicKey,
  /** The output mint */
  vaultAssetMint: PublicKey,
  /** The amount to withdraw */
  withdrawAmount: BN;
  /** The program ID of the Marginfi protocol */
  protocolProgram: PublicKey;
  /** The bank account */
  bank: PublicKey;
  /** The marginfi account */
  marginfiAccount: PublicKey;
  /** The marginfi group account */
  marginfiGroup: PublicKey;
  /** The oracle account */
  oracle: PublicKey;
  /** Optional lookup table addresses */
  lookupTableAddresses?: string[];
}

/**
 * Parameters for withdrawing from a Klend strategy
 */
export interface KlendWithdrawParams {
  /** The Voltr client */ 
  vc: VoltrClient,
  /** The connection */
  connection: Connection,
  /** The vault address */
  vault: PublicKey,
  /** The payer keypair */
  payerKp: Keypair,
  /** The asset token program */
  vaultAssetTokenProgram: PublicKey,
  /** The output mint */
  vaultAssetMint: PublicKey,
  /** The amount to withdraw */
  withdrawAmount: BN;
  /** The program ID of the Klend protocol */
  protocolProgram: PublicKey;
  /** The lending market account */
  lendingMarket: PublicKey;
  /** The reserve account */
  reserve: PublicKey;
  /** The scope prices account */
  scopePrices: PublicKey;
  /** Optional lookup table addresses */
  lookupTableAddresses?: string[];
}

/**
 * Parameters for withdrawing from a Drift strategy
 */
export interface DriftWithdrawParams {
  /** The Voltr client */ 
  vc: VoltrClient,
  /** The connection */
  connection: Connection,
  /** The vault address */
  vault: PublicKey,
  /** The payer keypair */
  payerKp: Keypair,
  /** The asset token program */
  vaultAssetTokenProgram: PublicKey,
  /** The output mint */
  vaultAssetMint: PublicKey,
  /** The amount to withdraw */
  withdrawAmount: BN;
  /** The program ID of the Drift protocol */
  protocolProgram: PublicKey;
  /** The state account */
  state: PublicKey;
  /** The market index */
  marketIndex: BN;
  /** The sub account ID */
  subAccountId: BN;
  /** The oracle account */
  oracle: PublicKey;
  /** Optional lookup table addresses */
  lookupTableAddresses?: string[];
}

/**
 * Union type for all withdraw strategy parameters
 */
export type WithdrawStrategyParams = 
  | { type: 'solend', params: SolendWithdrawParams }
  | { type: 'marginfi', params: MarginfiWithdrawParams }
  | { type: 'klend', params: KlendWithdrawParams }
  | { type: 'drift', params: DriftWithdrawParams };

/**
 * Simplified parameters for withdrawing from any strategy
 * Uses a consistent format for all strategy types
 */
export interface WithdrawParams {
  /** The Voltr client */ 
  vc: VoltrClient,
  /** The connection */
  connection: Connection,
  /** The vault address */
  vault: PublicKey,
  /** The payer keypair */
  payerKp: Keypair,
  /** The asset token program */
  vaultAssetTokenProgram: PublicKey,
  /** The output mint */
  vaultAssetMint: PublicKey,
  /** The strategy type: 'solend', 'marginfi', 'klend', or 'drift' */
  type: 'solend' | 'marginfi' | 'klend' | 'drift';
  /** The token to withdraw (e.g., 'USDC', 'USDT') */
  token: string;
  /** The address related to the strategy (e.g., lending market address) */
  address: string;
  /** The amount to withdraw (in the smallest denomination, e.g., 1000000 = 1 USDC) */
  amount: number;
}

const withdrawSolendStrategy = async (
  vc: VoltrClient,
  connection: Connection,
  vault: PublicKey,
  vaultAssetTokenProgram: PublicKey,
  vaultAssetMint: PublicKey,
  payerKp: Keypair,
  withdrawAmount: BN,
  protocolProgram: PublicKey,
  counterPartyTa: PublicKey,
  lendingMarket: PublicKey,
  reserve: PublicKey,
  collateralMint: PublicKey,
  pythOracle: PublicKey,
  switchboardOracle: PublicKey,
  lookupTableAddresses: string[] = []
) => {
  const [strategy] = PublicKey.findProgramAddressSync(
    [SEEDS.STRATEGY, counterPartyTa.toBuffer()],
    LENDING_ADAPTOR_PROGRAM_ID
  );

  const { vaultStrategyAuth } = vc.findVaultStrategyAddresses(vault, strategy);

  let transactionIxs: TransactionInstruction[] = [];

  const vaultCollateralAta = await setupTokenAccount(
    connection,
    payerKp.publicKey,
    collateralMint,
    vaultStrategyAuth,
    transactionIxs
  );

  const _vaultStrategyAssetAta = await setupTokenAccount(
    connection,
    payerKp.publicKey,
    vaultAssetMint,
    vaultStrategyAuth,
    transactionIxs,
    vaultAssetTokenProgram
  );

  const counterPartyTaAuth = await getAccount(
    connection,
    counterPartyTa,
    "confirmed",
    vaultOutputTokenProgram
  ).then((account) => account.owner);

  const remainingAccounts = [
    { pubkey: counterPartyTaAuth, isSigner: false, isWritable: true },
    { pubkey: counterPartyTa, isSigner: false, isWritable: true },
    { pubkey: protocolProgram, isSigner: false, isWritable: false },
    { pubkey: vaultCollateralAta, isSigner: false, isWritable: true },
    { pubkey: reserve, isSigner: false, isWritable: true },
    { pubkey: collateralMint, isSigner: false, isWritable: true },
    { pubkey: lendingMarket, isSigner: false, isWritable: true },
    { pubkey: pythOracle, isSigner: false, isWritable: false },
    { pubkey: switchboardOracle, isSigner: false, isWritable: false },
    { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
  ];

  let additionalArgs = Buffer.from([]); // No base additional args for Solend
  let addressLookupTableAccounts: AddressLookupTableAccount[] = [];

  if (outputMintAddress !== assetMintAddress) {
    const {
      additionalArgs: additionalArgsTemp,
      addressLookupTableAccounts: addressLookupTableAccountsTemp,
    } = await setupJupiterSwapForWithdrawStrategy(
      connection,
      withdrawAmount,
      new BN(0),
      counterPartyTa,
      vaultStrategyAuth,
      additionalArgs,
      remainingAccounts,
      transactionIxs,
      lookupTableAddresses
    );
    additionalArgs = additionalArgsTemp;
    addressLookupTableAccounts = addressLookupTableAccountsTemp;
  }

  const createWithdrawStrategyIx = await vc.createWithdrawStrategyIx(
    { withdrawAmount, additionalArgs },
    {
      manager: payerKp.publicKey,
      vault,
      vaultAssetMint,
      assetTokenProgram: new PublicKey(assetTokenProgram),
      strategy,
      remainingAccounts,
    }
  );

  transactionIxs.push(createWithdrawStrategyIx);

  const txSig = await sendAndConfirmOptimisedTx(
    transactionIxs,
    heliusRpcUrl,
    payerKp,
    [],
    addressLookupTableAccounts
  );
  console.log("Solend strategy withdrawn with signature:", txSig);
  return txSig;
};

const withdrawMarginfiStrategy = async (
  vc: VoltrClient,
  connection: Connection,
  vault: PublicKey,
  vaultAssetTokenProgram: PublicKey,
  vaultAssetMint: PublicKey,
  payerKp: Keypair,
  withdrawAmount: BN,
  protocolProgram: PublicKey,
  bank: PublicKey,
  marginfiAccount: PublicKey,
  marginfiGroup: PublicKey,
  oracle: PublicKey,
  lookupTableAddresses: string[] = []
) => {
  const [counterPartyTa] = PublicKey.findProgramAddressSync(
    [Buffer.from("liquidity_vault"), bank.toBuffer()],
    protocolProgram
  );

  const [strategy] = PublicKey.findProgramAddressSync(
    [SEEDS.STRATEGY, counterPartyTa.toBuffer()],
    LENDING_ADAPTOR_PROGRAM_ID
  );

  const { vaultStrategyAuth } = vc.findVaultStrategyAddresses(vault, strategy);

  let transactionIxs: TransactionInstruction[] = [];

  const vaultStrategyAssetAta = await setupTokenAccount(
    connection,
    payerKp.publicKey,
    vaultAssetMint,
    vaultStrategyAuth,
    transactionIxs,
    vaultAssetTokenProgram
  );

  const counterPartyTaAuth = await getAccount(
    connection,
    counterPartyTa,
    "confirmed",
    vaultOutputTokenProgram
  ).then((account) => account.owner);

  const remainingAccounts = [
    { pubkey: counterPartyTaAuth, isSigner: false, isWritable: true },
    { pubkey: counterPartyTa, isSigner: false, isWritable: true },
    { pubkey: protocolProgram, isSigner: false, isWritable: false },
    { pubkey: marginfiGroup, isSigner: false, isWritable: true },
    { pubkey: marginfiAccount, isSigner: false, isWritable: true },
    { pubkey: bank, isSigner: false, isWritable: true },
    { pubkey: oracle, isSigner: false, isWritable: false },
  ];

  let additionalArgs = Buffer.from([]); // No base additional args for Marginfi
  let addressLookupTableAccounts: AddressLookupTableAccount[] = [];

  if (outputMintAddress !== assetMintAddress) {
    const {
      additionalArgs: additionalArgsTemp,
      addressLookupTableAccounts: addressLookupTableAccountsTemp,
    } = await setupJupiterSwapForWithdrawStrategy(
      connection,
      withdrawAmount,
      new BN(0),
      counterPartyTa,
      vaultStrategyAuth,
      additionalArgs,
      remainingAccounts,
      transactionIxs,
      lookupTableAddresses
    );
    additionalArgs = additionalArgsTemp;
    addressLookupTableAccounts = addressLookupTableAccountsTemp;
  }

  const createWithdrawStrategyIx = await vc.createWithdrawStrategyIx(
    { withdrawAmount, additionalArgs },
    {
      manager: payerKp.publicKey,
      vault,
      vaultAssetMint,
      assetTokenProgram: new PublicKey(assetTokenProgram),
      strategy,
      remainingAccounts,
    }
  );

  transactionIxs.push(createWithdrawStrategyIx);

  const txSig = await sendAndConfirmOptimisedTx(
    transactionIxs,
    heliusRpcUrl,
    payerKp,
    [],
    addressLookupTableAccounts
  );
  console.log("Marginfi strategy withdrawn with signature:", txSig);
  return txSig;
};

const withdrawKlendStrategy = async (
  vc: VoltrClient,
  connection: Connection,
  vault: PublicKey,
  vaultAssetTokenProgram: PublicKey,
  vaultAssetMint: PublicKey,
  payerKp: Keypair,
  withdrawAmount: BN,
  protocolProgram: PublicKey,
  lendingMarket: PublicKey,
  reserve: PublicKey,
  scopePrices: PublicKey,
  lookupTableAddresses: string[] = []
) => {
  const [counterPartyTa] = PublicKey.findProgramAddressSync(
    [
      Buffer.from("reserve_liq_supply"),
      lendingMarket.toBuffer(),
      vaultOutputMint.toBuffer(),
    ],
    protocolProgram
  );

  const [strategy] = PublicKey.findProgramAddressSync(
    [SEEDS.STRATEGY, counterPartyTa.toBuffer()],
    LENDING_ADAPTOR_PROGRAM_ID
  );

  const { vaultStrategyAuth } = vc.findVaultStrategyAddresses(vault, strategy);
  const [reserveCollateralMint] = PublicKey.findProgramAddressSync(
    [
      Buffer.from("reserve_coll_mint"),
      lendingMarket.toBuffer(),
      vaultOutputMint.toBuffer(),
    ],
    protocolProgram
  );

  let transactionIxs: TransactionInstruction[] = [];

  const userDestinationCollateral = await setupTokenAccount(
    connection,
    payerKp.publicKey,
    reserveCollateralMint,
    vaultStrategyAuth,
    transactionIxs
  );

  const _vaultStrategyAssetAta = await setupTokenAccount(
    connection,
    payerKp.publicKey,
    vaultAssetMint,
    vaultStrategyAuth,
    transactionIxs,
    vaultAssetTokenProgram
  );

  const counterPartyTaAuth = await getAccount(
    connection,
    counterPartyTa,
    "confirmed",
    vaultOutputTokenProgram
  ).then((account) => account.owner);

  const remainingAccounts = [
    { pubkey: counterPartyTaAuth, isSigner: false, isWritable: true },
    { pubkey: counterPartyTa, isSigner: false, isWritable: true },
    { pubkey: protocolProgram, isSigner: false, isWritable: false },
    { pubkey: lendingMarket, isSigner: false, isWritable: false },
    { pubkey: reserve, isSigner: false, isWritable: true },
    { pubkey: reserveCollateralMint, isSigner: false, isWritable: true },
    {
      pubkey: userDestinationCollateral,
      isSigner: false,
      isWritable: true,
    },
    { pubkey: TOKEN_PROGRAM_ID, isSigner: false, isWritable: false },
    {
      pubkey: SYSVAR_INSTRUCTIONS_PUBKEY,
      isSigner: false,
      isWritable: false,
    },
    { pubkey: scopePrices, isSigner: false, isWritable: false },
  ];

  let additionalArgs = Buffer.from([]); // No base additional args for Klend
  let addressLookupTableAccounts: AddressLookupTableAccount[] = [];

  if (outputMintAddress !== assetMintAddress) {
    const {
      additionalArgs: additionalArgsTemp,
      addressLookupTableAccounts: addressLookupTableAccountsTemp,
    } = await setupJupiterSwapForWithdrawStrategy(
      connection,
      withdrawAmount,
      new BN(0),
      counterPartyTa,
      vaultStrategyAuth,
      additionalArgs,
      remainingAccounts,
      transactionIxs,
      lookupTableAddresses
    );
    additionalArgs = additionalArgsTemp;
    addressLookupTableAccounts = addressLookupTableAccountsTemp;
  }

  const createWithdrawStrategyIx = await vc.createWithdrawStrategyIx(
    { withdrawAmount, additionalArgs },
    {
      manager: payerKp.publicKey,
      vault,
      vaultAssetMint,
      assetTokenProgram: new PublicKey(assetTokenProgram),
      strategy,
      remainingAccounts,
    }
  );

  transactionIxs.push(createWithdrawStrategyIx);

  const txSig = await sendAndConfirmOptimisedTx(
    transactionIxs,
    heliusRpcUrl,
    payerKp,
    [],
    addressLookupTableAccounts
  );
  console.log("Klend strategy withdrawn with signature:", txSig);
  return txSig;
};

const withdrawDriftStrategy = async (
  vc: VoltrClient,
  connection: Connection,
  vault: PublicKey,
  vaultAssetTokenProgram: PublicKey,
  vaultAssetMint: PublicKey,
  payerKp: Keypair,
  withdrawAmount: BN,
  protocolProgram: PublicKey,
  state: PublicKey,
  marketIndex: BN,
  subAccountId: BN,
  oracle: PublicKey,
  lookupTableAddresses: string[] = []
) => {
  const [counterPartyTa] = PublicKey.findProgramAddressSync(
    [
      Buffer.from("spot_market_vault"),
      marketIndex.toArrayLike(Buffer, "le", 2),
    ],
    protocolProgram
  );

  const [strategy] = PublicKey.findProgramAddressSync(
    [SEEDS.STRATEGY, counterPartyTa.toBuffer()],
    LENDING_ADAPTOR_PROGRAM_ID
  );

  const { vaultStrategyAuth } = vc.findVaultStrategyAddresses(vault, strategy);
  const [userStats] = PublicKey.findProgramAddressSync(
    [Buffer.from("user_stats"), vaultStrategyAuth.toBuffer()],
    protocolProgram
  );

  const [user] = PublicKey.findProgramAddressSync(
    [
      Buffer.from("user"),
      vaultStrategyAuth.toBuffer(),
      subAccountId.toArrayLike(Buffer, "le", 2),
    ],
    protocolProgram
  );
  const [spotMarket] = PublicKey.findProgramAddressSync(
    [Buffer.from("spot_market"), marketIndex.toArrayLike(Buffer, "le", 2)],
    protocolProgram
  );

  let transactionIxs: TransactionInstruction[] = [];

  const _vaultStrategyAssetAta = await setupTokenAccount(
    connection,
    payerKp.publicKey,
    vaultAssetMint,
    vaultStrategyAuth,
    transactionIxs,
    vaultAssetTokenProgram
  );

  const counterPartyTaAuth = await getAccount(
    connection,
    counterPartyTa,
    "confirmed",
    vaultOutputTokenProgram
  ).then((account) => account.owner);

  const remainingAccounts = [
    { pubkey: counterPartyTaAuth, isSigner: false, isWritable: true },
    { pubkey: counterPartyTa, isSigner: false, isWritable: true },
    { pubkey: protocolProgram, isSigner: false, isWritable: false },
    { pubkey: state, isSigner: false, isWritable: false },
    { pubkey: user, isSigner: false, isWritable: true },
    { pubkey: userStats, isSigner: false, isWritable: true },
    { pubkey: oracle, isSigner: false, isWritable: false },
    { pubkey: spotMarket, isSigner: false, isWritable: true },
  ];

  let additionalArgs = Buffer.from([
    ...marketIndex.toArrayLike(Buffer, "le", 2),
  ]);
  let addressLookupTableAccounts: AddressLookupTableAccount[] = [];

  if (outputMintAddress !== assetMintAddress) {
    const {
      additionalArgs: additionalArgsTemp,
      addressLookupTableAccounts: addressLookupTableAccountsTemp,
    } = await setupJupiterSwapForWithdrawStrategy(
      connection,
      withdrawAmount,
      new BN(0),
      counterPartyTa,
      vaultStrategyAuth,
      additionalArgs,
      remainingAccounts,
      transactionIxs,
      lookupTableAddresses
    );
    additionalArgs = additionalArgsTemp;
    addressLookupTableAccounts = addressLookupTableAccountsTemp;
  }

  const createWithdrawStrategyIx = await vc.createWithdrawStrategyIx(
    {
      withdrawAmount,
      additionalArgs,
    },
    {
      manager: payerKp.publicKey,
      vault,
      vaultAssetMint,
      assetTokenProgram: new PublicKey(assetTokenProgram),
      strategy,
      remainingAccounts,
    }
  );

  transactionIxs.push(createWithdrawStrategyIx);

  const txSig = await sendAndConfirmOptimisedTx(
    transactionIxs,
    heliusRpcUrl,
    payerKp,
    [],
    addressLookupTableAccounts
  );
  console.log("Drift strategy withdrawn with signature:", txSig);
  return txSig;
};

/**
 * Wrapper function to withdraw from a strategy using simplified parameters
 * @param params The simplified parameters for the strategy
 * @returns A promise that resolves to the transaction signature
 */
export const withdraw = async (params: WithdrawParams): Promise<string> => {
  try {
    const {vc, connection, vault, vaultAssetTokenProgram, vaultAssetMint, payerKp, type, token, address, amount } = params;
    
    // Override the global withdraw amount with the provided amount
    const customWithdrawAmount = new BN(amount);
    
    // Convert token to uppercase for comparison
    const tokenUpperCase = token.toUpperCase();
    
    switch (type) {
      case 'solend': {
        // Create the address from the provided address string
        const lendingMarket = new PublicKey(address);
        
        // Check if token is supported for Solend
        if (tokenUpperCase !== 'USDC' && tokenUpperCase !== 'USDT' && 
            tokenUpperCase !== 'SOL' && tokenUpperCase !== 'USDS') {
          throw new Error(`Token ${token} not supported for Solend strategy`);
        }
        
        // Get token-specific constants using type safety
        const solendConstants = PROTOCOL_CONSTANTS.SOLEND.MAIN_MARKET[tokenUpperCase as 'USDC' | 'USDT' | 'SOL' | 'USDS'];
        
        const counterPartyTa = new PublicKey(solendConstants.COUNTERPARTY_TA);
        const reserve = new PublicKey(solendConstants.RESERVE);
        const collateralMint = new PublicKey(solendConstants.COLLATERAL_MINT);
        const pythOracle = new PublicKey(solendConstants.PYTH_ORACLE);
        const switchboardOracle = new PublicKey(solendConstants.SWITCHBOARD_ORACLE);
        
        const lookupTableAddresses = useLookupTable
          ? [...PROTOCOL_CONSTANTS.SOLEND.LOOKUP_TABLE_ADDRESSES, lookupTableAddress]
          : [...PROTOCOL_CONSTANTS.SOLEND.LOOKUP_TABLE_ADDRESSES];
        
        const txSig = await withdrawSolendStrategy(
          vc,
          connection,
          vault,
          vaultAssetTokenProgram,
          vaultAssetMint,
          payerKp,
          customWithdrawAmount,
          new PublicKey(PROTOCOL_CONSTANTS.SOLEND.PROGRAM_ID),
          counterPartyTa,
          lendingMarket,
          reserve,
          collateralMint,
          pythOracle,
          switchboardOracle,
          lookupTableAddresses
        );
        
        return txSig;
      }
      
      case 'marginfi': {
        // Create the address from the provided address string (bank address)
        const bank = new PublicKey(address);
        
        // Check if token is supported for Marginfi
        if (tokenUpperCase !== 'USDC' && tokenUpperCase !== 'USDT' && 
            tokenUpperCase !== 'SOL' && tokenUpperCase !== 'PYUSD' && 
            tokenUpperCase !== 'USDS') {
          throw new Error(`Token ${token} not supported for Marginfi strategy`);
        }
        
        // Get token-specific constants using type safety
        const marginfiConstants = PROTOCOL_CONSTANTS.MARGINFI.MAIN_MARKET[tokenUpperCase as 'USDC' | 'USDT' | 'SOL' | 'PYUSD' | 'USDS'];
        
        const marginfiGroupAddress = new PublicKey(PROTOCOL_CONSTANTS.MARGINFI.MAIN_MARKET.GROUP);
        const oracle = new PublicKey(marginfiConstants.ORACLE);
        
        const lookupTableAddresses = useLookupTable
          ? [...PROTOCOL_CONSTANTS.MARGINFI.LOOKUP_TABLE_ADDRESSES, lookupTableAddress]
          : [...PROTOCOL_CONSTANTS.MARGINFI.LOOKUP_TABLE_ADDRESSES];
        
        const txSig = await withdrawMarginfiStrategy(
          vc,
          connection,
          vault,
          vaultAssetTokenProgram,
          vaultAssetMint,
          payerKp,
          customWithdrawAmount,
          new PublicKey(PROTOCOL_CONSTANTS.MARGINFI.PROGRAM_ID),
          bank,
          new PublicKey(marginfiAccount),
          marginfiGroupAddress,
          oracle,
          lookupTableAddresses
        );
        
        return txSig;
      }
      
      case 'klend': {
        // Create the address from the provided address string (lending market)
        const lendingMarket = new PublicKey(address);
        
        // Check if token is supported for Klend
        if (tokenUpperCase !== 'USDC' && tokenUpperCase !== 'USDT' && 
            tokenUpperCase !== 'SOL' && tokenUpperCase !== 'PYUSD' && 
            tokenUpperCase !== 'USDS' && tokenUpperCase !== 'USDG') {
          throw new Error(`Token ${token} not supported for Klend strategy`);
        }
        
        // Get token-specific constants using type safety
        const klendConstants = PROTOCOL_CONSTANTS.KLEND.MAIN_MARKET[tokenUpperCase as 'USDC' | 'USDT' | 'SOL' | 'PYUSD' | 'USDS' | 'USDG'];
        
        const reserve = new PublicKey(klendConstants.RESERVE);
        const scopePrices = new PublicKey(PROTOCOL_CONSTANTS.KLEND.SCOPE_ORACLE);
        
        const lookupTableAddresses = useLookupTable
          ? [...PROTOCOL_CONSTANTS.KLEND.LOOKUP_TABLE_ADDRESSES, lookupTableAddress]
          : [...PROTOCOL_CONSTANTS.KLEND.LOOKUP_TABLE_ADDRESSES];
        
        const txSig = await withdrawKlendStrategy(
          vc,
          connection,
          vault,
          vaultAssetTokenProgram,
          vaultAssetMint,
          payerKp,
          customWithdrawAmount,
          new PublicKey(PROTOCOL_CONSTANTS.KLEND.PROGRAM_ID),
          lendingMarket,
          reserve,
          scopePrices,
          lookupTableAddresses
        );
        
        return txSig;
      }
      
      case 'drift': {
        // Create the address from the provided address string (state)
        const state = new PublicKey(address);
        
        // Check if token is supported for Drift
        if (tokenUpperCase !== 'USDC' && tokenUpperCase !== 'USDT' && 
            tokenUpperCase !== 'SOL' && tokenUpperCase !== 'PYUSD' && 
            tokenUpperCase !== 'USDS') {
          throw new Error(`Token ${token} not supported for Drift strategy`);
        }
        
        // Get token-specific constants using type safety
        const driftConstants = PROTOCOL_CONSTANTS.DRIFT.SPOT[tokenUpperCase as 'USDC' | 'USDT' | 'SOL' | 'PYUSD' | 'USDS'];
        
        const marketIndex = new BN(driftConstants.MARKET_INDEX);
        const oracle = new PublicKey(driftConstants.ORACLE);
        const subAccountId = new BN(PROTOCOL_CONSTANTS.DRIFT.SUB_ACCOUNT_ID);
        
        const lookupTableAddresses = useLookupTable
          ? [...PROTOCOL_CONSTANTS.DRIFT.LOOKUP_TABLE_ADDRESSES, lookupTableAddress]
          : [...PROTOCOL_CONSTANTS.DRIFT.LOOKUP_TABLE_ADDRESSES];
        
        const txSig = await withdrawDriftStrategy(
          vc,
          connection,
          vault,
          vaultAssetTokenProgram,
          vaultAssetMint,
          payerKp,
          customWithdrawAmount,
          new PublicKey(PROTOCOL_CONSTANTS.DRIFT.PROGRAM_ID),
          state,
          marketIndex,
          subAccountId,
          oracle,
          lookupTableAddresses
        );
        
        return txSig;
      }
      
      default:
        throw new Error(`Strategy type ${type} not supported`);
    }
  } catch (error) {
    console.error(`Error withdrawing from ${params.type} strategy:`, error);
    throw error;
  }
};

/**
 * Main function to withdraw from all strategies
 */
export const main = async () => {
  const connection = new Connection(heliusRpcUrl);
  const vc = new VoltrClient(connection);
  const vault = new PublicKey(vaultAddress);
  const vaultAssetTokenProgramPubkey = new PublicKey(assetTokenProgram);
  const vaultAssetMintPubkey = new PublicKey(outputMintAddress);
  
  const strategies = [
    {
      type: 'solend' as const,
      token: 'USDC',
      address: PROTOCOL_CONSTANTS.SOLEND.MAIN_MARKET.LENDING_MARKET,
      amount: withdrawAssetAmountPerStrategy,
      vaultAssetTokenProgram: vaultAssetTokenProgramPubkey,
      vaultAssetMint: vaultAssetMintPubkey,
    },
    {
      type: 'marginfi' as const,
      token: 'USDC',
      address: PROTOCOL_CONSTANTS.MARGINFI.MAIN_MARKET.USDC.BANK,
      amount: withdrawAssetAmountPerStrategy,
      vaultAssetTokenProgram: vaultAssetTokenProgramPubkey,
      vaultAssetMint: vaultAssetMintPubkey,
    },
    {
      type: 'klend' as const,
      token: 'USDC',
      address: PROTOCOL_CONSTANTS.KLEND.MAIN_MARKET.LENDING_MARKET,
      amount: withdrawAssetAmountPerStrategy,
      vaultAssetTokenProgram: vaultAssetTokenProgramPubkey,
      vaultAssetMint: vaultAssetMintPubkey,
    },
    {
      type: 'drift' as const,
      token: 'USDC',
      address: PROTOCOL_CONSTANTS.DRIFT.SPOT.STATE,
      amount: withdrawAssetAmountPerStrategy,
      vaultAssetTokenProgram: vaultAssetTokenProgramPubkey,
      vaultAssetMint: vaultAssetMintPubkey,
    },
  ];

  for (const strategy of strategies) {
    try {
      const result = await withdraw({
        vc,
        connection,
        vault,
        payerKp,
        type: strategy.type,
        token: strategy.token,
        address: strategy.address,
        amount: strategy.amount,
        vaultAssetTokenProgram: strategy.vaultAssetTokenProgram,
        vaultAssetMint: strategy.vaultAssetMint,
      });
      console.log(`${strategy.type} strategy withdraw result:`, result);
    } catch (error) {
      console.error(`Error withdrawing from ${strategy.type} strategy:`, error);
    }
  }
};

main();