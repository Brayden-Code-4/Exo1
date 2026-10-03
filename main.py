import os
import asyncio
import base64
from pathlib import Path
from dotenv import load_dotenv
from rodiumai import RodiumAI

load_dotenv()
client = RodiumAI(api_key= os.getenv("RODIUMAI_API_KEY"))

async def etape_1_chat():
    while True:
        print("\n Étape 1 : Chat ")
        question = input("Votre question : ").strip()
        if not question: continue

        # SDK flat API
        resp = await client.chat.completions.create(
            model="openai/gpt-4o",
            messages=[{"role": "user", "content": question}]
        )
        print(f"\n{resp.choices[0].message.content}")
        print(f"Coût : {getattr(resp, 'cost_rodi', 'N/A')} RODI")

        c = input("\nRester (r) ou passer à la suite (s)? ").lower()
        if c == 's': return 'next'
        if c == 'q': return 'quit'

async def etape_2_image():
    while True:
        print("\n Étape 2 : Image ")
        prompt = input("Décrivez l'image : ").strip()
        if not prompt: continue

        resp = await client.images.generate(
            model="openai/gpt-image-1-mini",
            prompt=prompt,
            size="1024x1024"
        )
        # le SDK retourne du b64_json
        Path("image.png").write_bytes(base64.b64decode(resp.data[0].b64_json))
        print("Image enregistrée : image.png")
        print(f"Coût : {getattr(resp, 'cost_rodi', 'N/A')} RODI")

        c = input("\nBack (b), rester (r), suite (s)? ").lower()
        if c == 's': return 'next'
        if c == 'b': return 'back'
        if c == 'q': return 'quit'

async def etape_3_video():
    while True:
        print("\n Étape 3 : Vidéo ")
        prompt = input("Décrivez la vidéo (4s) : ").strip()
        if not prompt: continue

        resp = await client.video.generations.create(
            model="openai/sora-2",
            prompt=prompt,
            duration_seconds=4,
            size="720x1280"
        )
        # peut être b64 ou url selon le modèle
        data = resp.data[0]
        if hasattr(data, 'b64_json') and data.b64_json:
            Path("video.mp4").write_bytes(base64.b64decode(data.b64_json))
        else:
            import requests
            r = requests.get(data.url)
            Path("video.mp4").write_bytes(r.content)
        print("Vidéo enregistrée : video.mp4")

        c = input("\nBack (b), rester (r), quitter (q)? ").lower()
        if c == 'b': return 'back'
        return 'quit'

async def main():
    etape = 1
    while True:
        if etape == 1:
            if await etape_1_chat() == 'next': etape = 2
            else: break
        elif etape == 2:
            res = await etape_2_image()
            if res == 'next': etape = 3
            elif res == 'back': etape = 1
            else: break
        elif etape == 3:
            if await etape_3_video() == 'back': etape = 2
            else: break

if __name__ == "__main__":
    asyncio.run(main())