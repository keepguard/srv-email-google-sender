#!/usr/bin/env python3
"""Script para testar se o TokenManager está sendo usado."""

import httpx
import asyncio
import json

async def test_token_manager_integration():
    """Testa se o srv-email-google-sender está usando o TokenManager."""
    
    print("🧪 Testando integração TokenManager...")
    
    # Teste 1: Verificar se srv-token-manager está funcionando
    print("\n1. Verificando srv-token-manager...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8700/health/")
            if response.status_code == 200:
                print("   ✅ srv-token-manager está funcionando")
            else:
                print(f"   ❌ srv-token-manager com problema: {response.status_code}")
                return
    except Exception as e:
        print(f"   ❌ Erro ao conectar com srv-token-manager: {e}")
        return
    
    # Teste 2: Verificar status do token
    print("\n2. Verificando status do token...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get("http://localhost:8700/api/v1/tokens/gmail/keepguard.ia@gmail.com/status")
            if response.status_code == 200:
                token_status = response.json()
                print(f"   ✅ Token válido: {token_status['is_valid']}")
                print(f"   ⏰ Expira em: {token_status['expires_in_minutes']} minutos")
            else:
                print(f"   ❌ Erro ao verificar token: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Erro ao verificar token: {e}")
    
    # Teste 3: Enviar e-mail e verificar logs
    print("\n3. Enviando e-mail...")
    try:
        async with httpx.AsyncClient() as client:
            email_data = {
                "to": "rafael.nogueira.soares@gmail.com",
                "subject": "Teste Integração TokenManager",
                "message": "Teste da integração",
                "html": "<h1>Teste</h1><p>Teste da integração</p>"
            }
            
            response = await client.post(
                "http://localhost:8602/send/mail",
                json=email_data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"   ✅ E-mail enviado com sucesso: {result['messageId']}")
            else:
                print(f"   ❌ Erro ao enviar e-mail: {response.status_code}")
                print(f"   Resposta: {response.text}")
    except Exception as e:
        print(f"   ❌ Erro ao enviar e-mail: {e}")
    
    # Teste 4: Verificar se houve chamadas ao TokenManager
    print("\n4. Verificando logs do srv-token-manager...")
    print("   📋 Verifique os logs do srv-token-manager para ver se houve chamadas")
    print("   💡 Se não houver logs de 'get_token' ou 'refresh_token', o TokenManager não está sendo usado")
    
    print("\n✅ Teste concluído!")

if __name__ == "__main__":
    asyncio.run(test_token_manager_integration())
