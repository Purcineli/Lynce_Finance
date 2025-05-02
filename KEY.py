import json

with open("credentials.json", "r") as f:
    creds = json.load(f)

# Corrigir o formato da chave
private_key = creds["private_key"].replace("\n", "\\n")
print(private_key)