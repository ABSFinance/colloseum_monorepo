
export const DRIFT = {
    PROGRAM_ID: "dRiftyHA39MWEi3m9aunc5MzRF1JYuBsbn6VPcn33UH",
    LOOKUP_TABLE_ADDRESSES: ["Fpys8GRa5RBWfyeN7AaDUwFGD1zkDCA4z3t4CJLV8dfL"],
    SUB_ACCOUNT_ID: 0,
    SPOT: {
      STATE: "5zpq7DvB6UdFFvpmBPspGPNfUGoBRRCE2HHg5u3gxcsN",
      SOL: {
        MARKET_INDEX: 1,
        ORACLE: "3m6i4RFWEDw2Ft4tFHPJtYgmpPe21k56M3FHeWYrgGBz",
      },
      USDC: {
        MARKET_INDEX: 0,
        ORACLE: "9VCioxmni2gDLv11qufWzT3RDERhQE4iY5Gf7NTfYyAV",
      },
      USDT: {
        MARKET_INDEX: 5,
        ORACLE: "JDKJSkxjasBGL3ce1pkrN6tqDzuVUZPWzzkGuyX8m9yN",
      },
      PYUSD: {
        MARKET_INDEX: 22,
        ORACLE: "5QZMnsyndmphvZF4BNgoMHwVZaREXeE2rpBoCPMxgCCd",
      },
      USDS: {
        MARKET_INDEX: 28,
        ORACLE: "7pT9mxKXyvfaZKeKy1oe2oV2K1RFtF7tPEJHUY3h2vVV",
      },
    },
  };

export const ORACLE = {
    SOL: {
        MINT: "So11111111111111111111111111111111111111112",
        PROGRAM_ID: "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
        PYTH_PULL_ORACLE: "7UVimffxr9ow1uXYxsr4LHAcV58mLzhmwaeKvJ1pjLiE",
        PYTH_FEED_ID:
        "0xef0d8b6fda2ceba41da15d4095d1da392a0d2f8ed0c6c7bc0f4cfac8c280b56d",
    },
    USDC: {
        MINT: "EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v",
        PROGRAM_ID: "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
        PYTH_PULL_ORACLE: "Dpw1EAVrSB1ibxiDQyTAW6Zip3J4Btk2x4SgApQCeFbX",
        PYTH_FEED_ID:
        "0xeaa020c61cc479712813461ce153894a96a6c00b21ed0cfc2798d1f9a9e9c94a",
    },
    USDT: {
        MINT: "Es9vMFrzaCERmJfrF4H2FYD4KCoNkY11McCe8BenwNYB",
        PROGRAM_ID: "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
        PYTH_PULL_ORACLE: "HT2PLQBcG5EiCcNSaMHAjSgd9F98ecpATbk4Sk5oYuM",
        PYTH_FEED_ID:
        "0x2b89b9dc8fdf9f34709a5b106b472f0f39bb6ca9ce04b0fd7f2e971688e2e53b",
    },
    PYUSD: {
        MINT: "2b1kV6DkPAnxd5ixfnxCpjxmKwqjjaYmCZfHsFu24GXo",
        PROGRAM_ID: "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb",
        PYTH_PULL_ORACLE: "9zXQxpYH3kYhtoybmZfUNNCRVuud7fY9jswTg1hLyT8k",
        PYTH_FEED_ID:
        "0xc1da1b73d7f01e7ddd54b3766cf7fcd644395ad14f70aa706ec5384c59e76692",
    },
    USDS: {
        MINT: "USDSwr9ApdHk5bvJKMjzff41FfuX8bSxdKcR81vTwcA",
        PROGRAM_ID: "TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA",
        PYTH_PULL_ORACLE: "DyYBBWEi9xZvgNAeMDCiFnmC1U9gqgVsJDXkL5WETpoX",
        PYTH_FEED_ID:
        "0x77f0971af11cc8bac224917275c1bf55f2319ed5c654a1ca955c82fa2d297ea1",
    },
    USDG: {
        MINT: "2u1tszSeqZ3qBWF3uNGPFc8TzMk2tdiwknnRMWGWjGWH",
        PROGRAM_ID: "TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb",
        PYTH_PULL_ORACLE: "6JkZmXGgWnzsyTQaqRARzP64iFYnpMNT4siiuUDUaB8s",
        PYTH_FEED_ID:
        "0xdaa58c6a3ce7d4b9c46c32a6e646012c17c4a2b24c08dd8c5e476118b855a7da",
    },
};
  
  export const JUPITER_SWAP = {
    PROGRAM_ID: "JUP6LkbZbjS1jKKwapdHNy74zcZ3tLUZoi5QNyVTaV4",
  };
  
  export const PROTOCOL_ADMIN = "vxyzZyfd6nJ3v82fTSmuRiKF4owWF9sAXqneu9mne9n";

  export const KLEND = {
    PROGRAM_ID: "KLend2g3cP87fffoy8q1mQqGKjrxjC8boSyAYavgmjD",
    SCOPE_ORACLE: "3NJYftD5sjVfxSnUdZ1wVML8f3aC6mp1CXCL6L7TnU8C",
    LOOKUP_TABLE_ADDRESSES: ["284iwGtA9X9aLy3KsyV8uT2pXLARhYbiSi5SiM2g47M2"],
    MAIN_MARKET: {
      LENDING_MARKET: "7u3HeHxYDLhnCoErrtycNokbQYbWGzLs6JSDqGAv5PfF",
      SOL: {
        RESERVE: "d4A2prbA2whesmvHaL88BH6Ewn5N4bTSU2Ze8P6Bc4Q",
      },
      USDC: {
        RESERVE: "D6q6wuQSrifJKZYpR1M8R4YawnLDtDsMmWM1NbBmgJ59",
      },
      USDT: {
        RESERVE: "H3t6qZ1JkguCNTi9uzVKqQ7dvt2cum4XiXWom6Gn5e5S",
      },
      PYUSD: {
        RESERVE: "2gc9Dm1eB6UgVYFBUN9bWks6Kes9PbWSaPaa9DqyvEiN",
      },
      USDS: {
        RESERVE: "BHUi32TrEsfN2U821G4FprKrR4hTeK4LCWtA3BFetuqA",
      },
      USDG: {
        RESERVE: "ESCkPWKHmgNE7Msf77n9yzqJd5kQVWWGy3o5Mgxhvavp",
      },
    },
    JITO_MARKET: {
      LENDING_MARKET: "H6rHXmXoCQvq8Ue81MqNh7ow5ysPa1dSozwW3PU1dDH6",
      SOL: {
        RESERVE: "6gTJfuPHEg6uRAijRkMqNc9kan4sVZejKMxmvx2grT1p",
      },
    },
    ALT_MARKET: {
      LENDING_MARKET: "ByYiZxp8QrdN9qbdtaAiePN8AAr3qvTPppNJDpf5DVJ5",
      PYUSD: {
        RESERVE: "D4c6nsTRjD2Kv7kYEUjtXiw72YKP8a1XHd33g38UpaV8",
      },
      USDC: {
        RESERVE: "9TD2TSv4pENb8VwfbVYg25jvym7HN6iuAR6pFNSrKjqQ",
      },
    },
    JLP_MARKET: {
      LENDING_MARKET: "DxXdAyU3kCjnyggvHmY5nAwg5cRbbmdyX3npfDMjjMek",
      USDT: {
        RESERVE: "2ov3CMqPBYG3jNBmmpXgK9KMW5GmU5GWZNGcwf7w3BC1",
      },
      PYUSD: {
        RESERVE: "FswUCVjvfAuzHCgPDF95eLKscGsLHyJmD6hzkhq26CLe",
      },
      USDC: {
        RESERVE: "Ga4rZytCpq1unD4DbEJ5bkHeUz9g3oh9AAFEi6vSauXp",
      },
      USDG: {
        RESERVE: "8rM1AY8M4YP4xNVmxhKnEUnj5CRWrcbcHpcgMoDfgqVi",
      },
    },
    ETHENA_MARKET: {
      LENDING_MARKET: "BJnbcRHqvppTyGesLzWASGKnmnF1wq9jZu6ExrjT7wvF",
      PYUSD: {
        RESERVE: "EDf6dGbVnCCABbNhE3mp5i1jV2JhDAVmTWb1ztij1Yhs",
      },
    },
  };

  export const MARGINFI = {
    PROGRAM_ID: "MFv2hWf31Z9kbCa1snEPYctwafyhdvnV7FZnsebVacA",
    LOOKUP_TABLE_ADDRESSES: ["HGmknUTUmeovMc9ryERNWG6UFZDFDVr9xrum3ZhyL4fC"],
    MAIN_MARKET: {
      GROUP: "4qp6Fx6tnZkY5Wropq9wUYgtFxXKwE6viZxFHg3rdAG8",
      SOL: {
        BANK: "CCKtUs6Cgwo4aaQUmBPmyoApH2gUDErxNZCAntD6LYGh",
        ORACLE: "7UVimffxr9ow1uXYxsr4LHAcV58mLzhmwaeKvJ1pjLiE",
      },
      USDC: {
        BANK: "2s37akK2eyBbp8DZgCm7RtsaEz8eJP3Nxd4urLHQv7yB",
        ORACLE: "Gnt27xtC473ZT2Mw5u8wZ68Z3gULkSTb5DuxJy7eJotD",
      },
      USDT: {
        BANK: "HmpMfL8942u22htC4EMiWgLX931g3sacXFR6KjuLgKLV",
        ORACLE: "HT2PLQBcG5EiCcNSaMHAjSgd9F98ecpATbk4Sk5oYuM",
      },
      PYUSD: {
        BANK: "8UEiPmgZHXXEDrqLS3oiTxQxTbeYTtPbeMBxAd2XGbpu",
        ORACLE: "A52UBHzxnKrH17zjhajRTgHcWwtxN7KYDAzBgraqFxQJ",
      },
      USDS: {
        BANK: "FDsf8sj6SoV313qrA91yms3u5b3P4hBxEPvanVs8LtJV",
        ORACLE: "DyYBBWEi9xZvgNAeMDCiFnmC1U9gqgVsJDXkL5WETpoX",
      },
    },
  };

  export const SOLEND = {
    PROGRAM_ID: "So1endDq2YkqhipRh3WViPa8hdiSpxWy6z3Z6tMCpAo",
    LOOKUP_TABLE_ADDRESSES: ["89ig7Cu6Roi9mJMqpY8sBkPYL2cnqzpgP16sJxSUbvct"],
    MAIN_MARKET: {
      LENDING_MARKET: "4UpD2fh7xH3VP9QQaXtsS1YY3bxzWhtfpks7FatyKvdY",
      SOL: {
        COUNTERPARTY_TA: "8UviNr47S8eL6J3WfDxMRa3hvLta1VDJwNWqsDgtN3Cv",
        RESERVE: "8PbodeaosQP19SjYFx855UMqWxH2HynZLdBXmsrbac36",
        COLLATERAL_MINT: "5h6ssFpeDeRbzsEHDbTQNH7nVGgsKrZydxdSTnLm6QdV",
        PYTH_ORACLE: "7UVimffxr9ow1uXYxsr4LHAcV58mLzhmwaeKvJ1pjLiE",
        SWITCHBOARD_ORACLE: "GvDMxPzN1sCj7L26YDK2HnMRXEQmQ2aemov8YBtPS7vR",
      },
      USDC: {
        COUNTERPARTY_TA: "8SheGtsopRUDzdiD6v6BR9a6bqZ9QwywYQY99Fp5meNf",
        RESERVE: "BgxfHJDzm44T7XG68MYKx7YisTjZu73tVovyZSjJMpmw",
        COLLATERAL_MINT: "993dVFL2uXWYeoXuEBFXR4BijeXdTv4s6BzsCjJZuwqk",
        PYTH_ORACLE: "Dpw1EAVrSB1ibxiDQyTAW6Zip3J4Btk2x4SgApQCeFbX",
        SWITCHBOARD_ORACLE: "BjUgj6YCnFBZ49wF54ddBVA9qu8TeqkFtkbqmZcee8uW",
      },
      USDT: {
        COUNTERPARTY_TA: "3CdpSW5dxM7RTxBgxeyt8nnnjqoDbZe48tsBs9QUrmuN",
        RESERVE: "8K9WC8xoh2rtQNY7iEGXtPvfbDCi563SdWhCAhuMP2xE",
        COLLATERAL_MINT: "BTsbZDV7aCMRJ3VNy9ygV4Q2UeEo9GpR8D6VvmMZzNr8",
        PYTH_ORACLE: "HT2PLQBcG5EiCcNSaMHAjSgd9F98ecpATbk4Sk5oYuM",
        SWITCHBOARD_ORACLE: "ETAaeeuQBwsh9mC2gCov9WdhJENZuffRMXY2HgjCcSL9",
      },
      USDS: {
        COUNTERPARTY_TA: "9uC55GXWnvc4XppM42CiLpyQ3KvVN3KtnLctvcH2HZCg",
        RESERVE: "HUL7GeHECRMbBFwde6pBmCPwDZjoLQDX7Xis4d64jAya",
        COLLATERAL_MINT: "2vtVnToA4N1FaxzYiwYVyRHY8jJAiaHrtdSycKNLDPRg",
        PYTH_ORACLE: "DyYBBWEi9xZvgNAeMDCiFnmC1U9gqgVsJDXkL5WETpoX",
        SWITCHBOARD_ORACLE: "nu11111111111111111111111111111111111111111",
      },
    },
  };

  export const PROTOCOL_CONSTANTS = {
    SOLEND,
    MARGINFI,
    DRIFT,
    KLEND,
  };