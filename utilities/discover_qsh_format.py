from scannerUtils import send_command
import time
from itertools import product

def discoverQSHVariants(ser, baseFreq=462550, delayBetween=0.1):
    """
    Focused brute-force discovery of QSH formats with modulation fixed to NFM.

    Tries different permutations of parameters and parameter lengths.
    """

    att_values = ["0", "1"]
    dly_values = ["-5", "0", "5"]
    code_search_values = ["0", "1"]
    fixed_mod = "NFM"

    base = str(baseFreq)
    tested = set()
    successes = []

    print("🔍 Starting QSH discovery (mod=NFM)...\n")

    for att, dly, code in product(att_values, dly_values, code_search_values):
        params = [base, "", fixed_mod, att, dly, "", code]

        # Generate truncated versions with varying argument count
        for n in range(1, len(params) + 1):
            partial = params[:n]
            cmd = "QSH," + ",".join(partial)
            if cmd in tested:
                continue
            tested.add(cmd)

            response = send_command(ser, cmd)
            if "OK" in response:
                print(f"✅ SUCCESS: {cmd} → {response}")
                successes.append((cmd, response))
            elif "ERR" in response or "NG" in response:
                print(f"❌ {cmd} → {response}")
            else:
                print(f"🟡 {cmd} → {response}")
                successes.append((cmd, response))

            time.sleep(delayBetween)

    print(f"\n✅ Discovery complete. {len(successes)} possible valid responses.")
    return successes
