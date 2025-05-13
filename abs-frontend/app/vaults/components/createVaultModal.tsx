"use client";

import { useState, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { z } from "zod";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Textarea } from "@/components/ui/textarea";
import {
  X,
  ChevronRight,
  ChevronDown,
  ChevronLeft,
  Search,
  AlertCircle,
} from "lucide-react";
import { Slider } from "@/components/ui/slider";
import { Card, CardContent } from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { BN } from "@coral-xyz/anchor";
import {
  ComputeBudgetProgram,
  Keypair,
  PublicKey,
  TransactionConfirmationStrategy,
  TransactionInstruction,
  TransactionMessage,
  VersionedTransaction,
} from "@solana/web3.js";
import {
  connection,
  useVoltrClientStore,
} from "@/components/hooks/useVoltrClientStore";
import { useSolanaWallets, usePrivy } from "@privy-io/react-auth";
import { supabase } from "@/lib/supabase";
import { useSendTransaction } from "@privy-io/react-auth/solana";

interface CreateVaultModalProps {
  isOpen: boolean;
  onClose: () => void;
}

interface AllocationItem {
  id: string;
  name: string;
  strategy: string;
  percentage: number;
  token?: string;
  tokenIcon?: string;
}

// Zod schemas for validation
const setupSchema = z.object({
  vaultName: z.string().min(1, "Vault name is required"),
  vaultDescription: z.string().min(1, "Description is required"),
  initialDeposit: z.string().min(1, "Initial deposit is required"),
});

export function CreateVaultModal({ isOpen, onClose }: CreateVaultModalProps) {
  const [activeTab, setActiveTab] = useState<
    "setup" | "allocation" | "preview"
  >("setup");
  const [vaultName, setVaultName] = useState<string>("");
  const [vaultDescription, setVaultDescription] = useState<string>("");
  const [initialDeposit, setInitialDeposit] = useState<string>("");
  const [errors, setErrors] = useState<Record<string, string>>({});
  const { sendTransaction } = useSendTransaction();

  const [allocations, setAllocations] = useState<AllocationItem[]>([
    {
      id: "1",
      name: "ABS",
      strategy: "Leverage and hedge JLP",
      percentage: 30,
      token: "USDC",
      tokenIcon: "U",
    },
    {
      id: "2",
      name: "ABS",
      strategy: "Stablecoin Yield",
      percentage: 30,
      token: "USDT",
      tokenIcon: "T",
    },
    {
      id: "3",
      name: "ABS",
      strategy: "Liquidity Provision",
      percentage: 40,
      token: "ETH",
      tokenIcon: "E",
    },
  ]);

  const { user, ready, authenticated } = usePrivy();
  const { wallets } = useSolanaWallets();
  const { sendTransaction: privySendTransaction } = useSendTransaction();
  const [isWalletReady, setIsWalletReady] = useState(false);
  const [currentWallet, setCurrentWallet] = useState<any>(null);

  useEffect(() => {
    const checkWallet = async () => {
      console.log("Checking Privy state:", {
        ready,
        authenticated,
        userAddress: user?.wallet?.address,
        wallets: wallets.map((w) => w.address),
      });

      if (!ready) {
        console.log("Privy not ready yet");
        return;
      }

      if (!authenticated) {
        console.log("User not authenticated with Privy");
        return;
      }

      if (wallets.length > 0) {
        const wallet = wallets[0];
        console.log("Using wallet:", wallet.address);
        setCurrentWallet(wallet);
        setIsWalletReady(true);
      } else {
        console.log("No wallets available");
        setCurrentWallet(null);
        setIsWalletReady(false);
      }
    };
    checkWallet();
  }, [wallets, ready, authenticated, user]);

  const client = useVoltrClientStore((state) => state.client);

  const totalAllocated = allocations.reduce(
    (sum, item) => sum + item.percentage,
    0
  );
  const isFullyAllocated = totalAllocated === 100;

  const validateSetup = () => {
    try {
      setupSchema.parse({
        vaultName,
        vaultDescription,
        initialDeposit,
      });
      setErrors({});
      return true;
    } catch (error) {
      if (error instanceof z.ZodError) {
        const newErrors: Record<string, string> = {};
        error.errors.forEach((err) => {
          if (err.path[0]) {
            newErrors[err.path[0].toString()] = err.message;
          }
        });
        setErrors(newErrors);
      }
      return false;
    }
  };

  const handleAllocationChange = (id: string, value: number) => {
    setAllocations((prev) =>
      prev.map((item) =>
        item.id === id ? { ...item, percentage: value } : item
      )
    );
  };

  const handleNext = () => {
    if (activeTab === "setup") {
      if (validateSetup()) {
        setActiveTab("allocation");
      }
    } else if (activeTab === "allocation") {
      if (isFullyAllocated) {
        setActiveTab("preview");
      }
    }
  };

  const handleBack = () => {
    if (activeTab === "allocation") setActiveTab("setup");
    else if (activeTab === "preview") setActiveTab("allocation");
  };
  const handleCreateVault = async () => {
    console.log("Create vault attempt:", {
      ready,
      authenticated,
      isWalletReady,
      currentWallet: currentWallet?.address,
      wallets: wallets.map((w) => w.address),
    });

    if (!ready || !authenticated) {
      console.log("Privy not ready or user not authenticated");
      return;
    }

    if (!isWalletReady || !currentWallet) {
      console.log("Wallet not ready or not connected");
      return;
    }

    const vaultParams = {
      config: {
        maxCap: new BN("1000000000"),
        startAtTs: new BN(Math.floor(Date.now() / 1000)),
        lockedProfitDegradationDuration: new BN(3600),
        managerManagementFee: 50,
        managerPerformanceFee: 1000,
        adminManagementFee: 50,
        adminPerformanceFee: 1000,
        redemptionFee: 10,
        issuanceFee: 10,
        withdrawalWaitingPeriod: new BN(3600),
      },
      name: vaultName,
      description: vaultDescription,
    };

    console.log("Vault Params:", vaultParams);
    console.log("Current wallet address:", currentWallet.address);

    const vaultKeypair = Keypair.generate();
    let payer = new PublicKey(currentWallet.address);

    try {
      const createInitializeVaultIx = await client?.createInitializeVaultIx(
        vaultParams,
        {
          vault: vaultKeypair.publicKey,
          vaultAssetMint: new PublicKey(
            "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v"
          ),
          admin: payer,
          manager: payer,
          payer: payer,
        }
      );

      const createAddAdaptorIx = await client?.createAddAdaptorIx({
        vault: vaultKeypair.publicKey,
        admin: payer,
        payer: payer,
      });

      if (!createInitializeVaultIx || !createAddAdaptorIx) {
        console.error("Failed to create vault initialization instruction");
        return;
      }

      const transactionIxs: TransactionInstruction[] = [];
      transactionIxs.push(createInitializeVaultIx);
      transactionIxs.push(createAddAdaptorIx);

      const modifyComputeUnits = ComputeBudgetProgram.setComputeUnitLimit({
        units: 400000,
      });

      const { lastValidBlockHeight, blockhash } =
        await connection.getLatestBlockhash();

      const messageV0 = new TransactionMessage({
        payerKey: payer,
        recentBlockhash: blockhash,
        instructions: [modifyComputeUnits, ...transactionIxs],
      }).compileToV0Message([]);

      const transaction = new VersionedTransaction(messageV0);
      transaction.sign([vaultKeypair]);

      console.log("Sending transaction with wallet:", currentWallet.address);

      try {
        const txSig = await currentWallet.sendTransaction(
          transaction,
          connection
        );
        console.log("Transaction sent with signature:", txSig);

        let retries = 3;
        let confirmed = false;

        while (retries > 0 && !confirmed) {
          try {
            const strategy: TransactionConfirmationStrategy = {
              signature: txSig,
              lastValidBlockHeight,
              blockhash: blockhash,
            };

            const confirmation = await connection.confirmTransaction(
              strategy,
              "confirmed"
            );
            if (confirmation.value.err) {
              throw new Error(`Transaction failed: ${confirmation.value.err}`);
            }
            confirmed = true;
            console.log("Transaction confirmed successfully");
          } catch (error) {
            console.log(
              `Confirmation attempt failed, retries left: ${retries - 1}`
            );
            retries--;
            if (retries === 0) {
              throw error;
            }
            // Wait before retrying
            await new Promise((resolve) => setTimeout(resolve, 2000));
          }
        }

        if (!confirmed) {
          console.log("Transaction confirmation failed after all retries");
        }

        try {
          const { data: latestPool, error: poolError } = await supabase
            .from("pool_info")
            .select("id")
            .eq("type", "abs_vault")
            .order("id", { ascending: false })
            .limit(1);

          if (poolError) {
            throw new Error(
              `Error fetching latest pool info: ${poolError.message}`
            );
          }

          const nextId =
            latestPool && latestPool.length > 0 ? latestPool[0].id + 1 : 1;

          const { error: poolInsertError } = await supabase
            .from("pool_info")
            .insert([
              {
                id: nextId,
                type: "abs_vault",
              },
            ]);

          if (poolInsertError) {
            throw new Error(
              `Error inserting into pool_info: ${poolInsertError.message}`
            );
          }

          const { error: vaultError } = await supabase
            .from("abs_vault_info")
            .insert([
              {
                name: vaultParams.name,
                address: vaultKeypair.publicKey.toBase58(),
                pool_id: nextId,
                org_id: 12,
                underlying_token:
                  "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
                capacity: vaultParams.config.maxCap.toString(),
                adaptors: ["kamino-lend", "save", "drift-vault"],
                allowed_pools: ["1088", "1101", "1071"],
              },
            ]);

          if (vaultError) {
            throw new Error(
              `Error storing vault in abs_vault_info: ${vaultError.message}`
            );
          }

          console.log("Vault successfully stored in both tables");
          onClose(); // Close the modal after successful storage
        } catch (error) {
          console.error("Error in vault storage process:", error);
          // You might want to add some UI feedback here for the error
        }
      } catch (error) {
        console.error("Error creating vault:", error);
      }
    } catch (error) {
      console.error("Error creating vault:", error);
    }

    onClose();
  };

  const handleRemoveAllocation = (id: string) => {
    setAllocations((prev) => prev.filter((item) => item.id !== id));
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <motion.div
          className="fixed inset-0 z-50 flex items-center justify-center bg-black/50"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
          onClick={onClose}
        >
          <motion.div
            className="relative w-full max-w-xl rounded-lg bg-[#1c1c1e] p-6 text-white shadow-xl"
            initial={{ scale: 0.9, opacity: 0 }}
            animate={{ scale: 1, opacity: 1 }}
            exit={{ scale: 0.9, opacity: 0 }}
            onClick={(e) => e.stopPropagation()}
          >
            <button
              onClick={onClose}
              className="absolute right-4 top-4 text-gray-400 hover:text-white"
            >
              <X className="h-5 w-5" />
            </button>

            <div className="mb-8 flex border-b border-gray-700">
              <button
                className={`flex-1 px-4 py-4 text-sm font-medium ${
                  activeTab === "setup"
                    ? "border-b-2 border-white"
                    : "text-gray-400"
                }`}
                onClick={() => setActiveTab("setup")}
              >
                Set Up
              </button>
              <button
                className={`flex-1 px-4 py-4 text-sm font-medium ${
                  activeTab === "allocation"
                    ? "border-b-2 border-white"
                    : "text-gray-400"
                }`}
                onClick={() => setActiveTab("allocation")}
              >
                Allocation
              </button>
              <button
                className={`flex-1 px-4 py-4 text-sm font-medium ${
                  activeTab === "preview"
                    ? "border-b-2 border-white"
                    : "text-gray-400"
                }`}
                onClick={() => setActiveTab("preview")}
              >
                Preview
              </button>
            </div>

            <div className="min-h-[400px]">
              {activeTab === "setup" && (
                <div className="space-y-6">
                  <div className="space-y-2">
                    <h3 className="text-lg font-medium">Vault Name</h3>
                    <p className="text-sm text-gray-400">
                      What do you want to name your vault?
                    </p>
                    <Input
                      placeholder="Type something"
                      className={`mt-2 bg-[#2c2c2e] border-0 text-white placeholder:text-gray-500 ${
                        errors.vaultName ? "ring-1 ring-red-500" : ""
                      }`}
                      value={vaultName}
                      onChange={(e) => setVaultName(e.target.value)}
                    />
                    {errors.vaultName && (
                      <p className="text-xs text-red-500 mt-1">
                        {errors.vaultName}
                      </p>
                    )}
                  </div>

                  <div className="space-y-2">
                    <h3 className="text-lg font-medium">Description</h3>
                    <p className="text-sm text-gray-400">
                      What do you want your vault to look like?
                    </p>
                    <Textarea
                      placeholder="Type something"
                      className={`mt-2 bg-[#2c2c2e] border-0 text-white placeholder:text-gray-500 min-h-[100px] ${
                        errors.vaultDescription ? "ring-1 ring-red-500" : ""
                      }`}
                      value={vaultDescription}
                      onChange={(e) => setVaultDescription(e.target.value)}
                    />
                    {errors.vaultDescription && (
                      <p className="text-xs text-red-500 mt-1">
                        {errors.vaultDescription}
                      </p>
                    )}
                  </div>

                  <div className="grid grid-cols-2 gap-6">
                    {/* Left Column */}
                    <div className="space-y-2">
                      <h3 className="text-lg font-medium">Underlying Token</h3>
                      <p className="text-sm text-gray-400">
                        Choose your preferred token
                      </p>
                      <button className="flex w-full items-center justify-between rounded bg-[#2c2c2e] px-4 py-2 text-white">
                        <div className="flex items-center">
                          <div className="mr-2 flex h-6 w-6 items-center justify-center rounded-full bg-blue-500 text-xs">
                            Ⓤ
                          </div>
                          USDC
                        </div>
                        <ChevronDown className="h-4 w-4 text-gray-400" />
                      </button>
                    </div>

                    {/* Right Column */}
                    <div className="space-y-2 mt-2">
                      <h3 className="text-lg font-medium">Initial Deposit</h3>
                      <div className="relative">
                        <Input
                          className={`bg-[#2c2c2e] pr-16 border-0 text-white ${
                            errors.initialDeposit ? "ring-1 ring-red-500" : ""
                          }`}
                          value={initialDeposit}
                          onChange={(e) => setInitialDeposit(e.target.value)}
                        />
                        <button className="absolute right-2 top-1/2 -translate-y-1/2 rounded bg-[#3c3c3e] px-2 py-1 text-xs">
                          Max
                        </button>
                      </div>
                      {errors.initialDeposit && (
                        <p className="text-xs text-red-500 mt-1">
                          {errors.initialDeposit}
                        </p>
                      )}
                      <div className="flex justify-between text-sm">
                        <span className="text-gray-400">Balance</span>
                        <div className="flex items-center">
                          <div className="mr-1 h-3 w-3 rounded-sm bg-teal-500" />
                          13,530
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === "allocation" && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-xl font-medium">Allocation</h3>
                    <p className="text-sm text-gray-400">
                      Allocate your funds across different strategies
                    </p>
                  </div>

                  <div className="relative">
                    <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-gray-500" />
                    <Input
                      placeholder="Search lending pools"
                      className="pl-9 bg-[#2c2c2e] border-0 text-white placeholder:text-gray-500"
                    />
                  </div>

                  <div className="flex justify-between items-center">
                    <h4 className="text-sm font-medium">Total Allocation</h4>
                    <Badge
                      variant={isFullyAllocated ? "default" : "destructive"}
                      className={`px-3 py-1 ${
                        isFullyAllocated ? "bg-green-600" : "bg-yellow-600"
                      }`}
                    >
                      {totalAllocated}% allocated
                    </Badge>
                  </div>

                  {!isFullyAllocated && (
                    <Alert
                      variant="destructive"
                      className="bg-yellow-100/90 text-yellow-800"
                    >
                      <AlertCircle className="h-4 w-4 font-bold" />
                      <AlertDescription>
                        <span className="text-yellow-800">
                          You must allocate exactly 100% before proceeding
                        </span>
                      </AlertDescription>
                    </Alert>
                  )}

                  <div className="space-y-4">
                    {allocations.map((allocation) => (
                      <div
                        key={allocation.id}
                        className="bg-[#2c2c2e] rounded-lg p-4"
                      >
                        <div className="flex justify-between items-center mb-3">
                          <div className="flex items-center gap-2">
                            <div className="h-8 w-8 rounded-full bg-blue-500 flex items-center justify-center">
                              <span className="text-xs">
                                {allocation.tokenIcon}
                              </span>
                            </div>
                            <div>
                              <div className="font-medium">
                                {allocation.name}
                              </div>
                              <div className="text-xs text-gray-400">
                                {allocation.strategy}
                              </div>
                            </div>
                          </div>
                          <div className="flex items-center gap-2">
                            <Badge variant="outline" className="bg-blue-300/90">
                              {allocation.percentage}%
                            </Badge>
                            <Button
                              variant="ghost"
                              size="icon"
                              className="h-6 w-6"
                              onClick={() =>
                                handleRemoveAllocation(allocation.id)
                              }
                            >
                              <ChevronDown className="h-4 w-4 text-gray-400" />
                            </Button>
                          </div>
                        </div>
                        <div className="pt-2">
                          <Slider
                            value={[allocation.percentage]}
                            min={0}
                            max={100}
                            step={1}
                            onValueChange={(value) =>
                              handleAllocationChange(allocation.id, value[0])
                            }
                            className="cursor-pointer"
                          />
                        </div>
                      </div>
                    ))}
                  </div>
                  {/* 
                  <div>
                    <div className="flex justify-between text-sm mb-2">
                      <span>Token Allocation</span>
                      <span className={isFullyAllocated ? "text-green-500" : "text-yellow-500"}>{totalAllocated}%</span>
                    </div>
                    <Progress value={totalAllocated} className="h-3 bg-[#2c2c2e]" />
                  </div> */}
                </div>
              )}

              {activeTab === "preview" && (
                <div className="space-y-6">
                  <div>
                    <h3 className="text-xl font-medium">Vault Preview</h3>
                    <p className="text-sm text-gray-400">
                      Review your vault configuration before creating
                    </p>
                  </div>

                  <Card className="bg-[#2c2c2e] border-0 overflow-hidden">
                    <CardContent>
                      <div className="flex justify-between items-start mb-4">
                        <div>
                          <h3 className="text-xl font-semibold text-white">
                            {vaultName || "Untitled Vault"}
                          </h3>
                          <p className="text-sm text-gray-400 mt-1">
                            {vaultDescription || "No description"}
                          </p>
                        </div>
                        <Badge className="bg-green-600">Ready</Badge>
                      </div>

                      <Separator className="my-4 bg-gray-700" />

                      <div className="space-y-4">
                        <div>
                          <h4 className="text-sm font-medium text-gray-400 mb-2">
                            Vault Details
                          </h4>
                          <div className="grid grid-cols-2 gap-4">
                            <div className="bg-[#3c3c3e] rounded-lg p-3">
                              <p className="text-xs text-gray-400">
                                Underlying Token
                              </p>
                              <div className="flex items-center mt-1">
                                <div className="mr-2 flex h-5 w-5 items-center justify-center rounded-full bg-blue-500 text-xs">
                                  Ⓤ
                                </div>
                                <span className="font-medium text-white">
                                  USDC
                                </span>
                              </div>
                            </div>
                            <div className="bg-[#3c3c3e] rounded-lg p-3">
                              <p className="text-xs text-gray-400">
                                Initial Deposit
                              </p>
                              <p className="font-medium mt-1 text-white">
                                {initialDeposit || "0"} USDC
                              </p>
                            </div>
                          </div>
                        </div>

                        <div>
                          <h4 className="text-sm font-medium text-gray-400 mb-2">
                            Allocation Strategy
                          </h4>
                          <div className="space-y-2">
                            {allocations.map((allocation, index) => (
                              <div
                                key={index}
                                className="flex items-center justify-between bg-[#3c3c3e] rounded-lg px-4 py-3"
                              >
                                <div className="flex items-center gap-3">
                                  <div className="h-6 w-6 rounded-full bg-blue-500 flex items-center justify-center">
                                    <span className="text-xs">
                                      {allocation.tokenIcon}
                                    </span>
                                  </div>
                                  <div>
                                    <div className="font-medium text-white">
                                      {allocation.name}
                                    </div>
                                    <div className="text-xs text-gray-400">
                                      {allocation.strategy}
                                    </div>
                                  </div>
                                </div>
                                <Badge
                                  variant="outline"
                                  className="bg-blue-100/90 border-blue-500/30"
                                >
                                  {allocation.percentage}%
                                </Badge>
                              </div>
                            ))}
                          </div>
                        </div>

                        <div>
                          <h4 className="text-sm font-medium text-gray-400 mb-2">
                            Allocation Distribution
                          </h4>
                          <div className="h-8 bg-[#3c3c3e] rounded-full overflow-hidden flex">
                            {allocations.map((allocation, index) => (
                              <div
                                key={index}
                                className="h-full flex items-center justify-center text-xs font-medium text-white"
                                style={{
                                  width: `${allocation.percentage}%`,
                                  backgroundColor:
                                    index === 0
                                      ? "#3b82f6"
                                      : index === 1
                                      ? "#6366f1"
                                      : "#8b5cf6",
                                }}
                              >
                                {allocation.percentage > 10
                                  ? `${allocation.percentage}%`
                                  : ""}
                              </div>
                            ))}
                          </div>
                        </div>
                      </div>
                    </CardContent>
                  </Card>
                </div>
              )}
            </div>

            <div className="mt-8 flex justify-between">
              {activeTab !== "setup" && (
                <Button
                  variant="outline"
                  onClick={handleBack}
                  className="border-gray-700 bg-zinc-800 text-white hover:bg-[#2c2c2e] hover:text-white"
                >
                  <ChevronLeft className="mr-2 h-4 w-4" /> Back
                </Button>
              )}
              {activeTab === "setup" && (
                <div></div> // Empty div to maintain flex spacing
              )}
              {activeTab !== "preview" ? (
                <Button
                  onClick={handleNext}
                  disabled={activeTab === "allocation" && !isFullyAllocated}
                  className="bg-slate-100 text-black cursor-pointer hover:bg-slate-200 disabled:bg-slate-100/50 disabled:text-black/50"
                >
                  Next <ChevronRight className="ml-2 h-4 w-4" />
                </Button>
              ) : (
                <Button
                  onClick={handleCreateVault}
                  className="bg-green-600 hover:bg-green-700 cursor-pointer"
                >
                  Create Vault
                </Button>
              )}
            </div>
          </motion.div>
        </motion.div>
      )}
    </AnimatePresence>
  );
}
