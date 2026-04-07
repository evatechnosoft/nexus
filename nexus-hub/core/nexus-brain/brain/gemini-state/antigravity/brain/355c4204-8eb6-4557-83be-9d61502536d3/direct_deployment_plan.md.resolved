# Direct Deployment to Azure Web App

The user wants to deploy the application directly from the local environment to Azure Web App, bypassing Azure DevOps pipelines.

## User Review Required

> [!IMPORTANT]
> Bu işlem için bilgisayarınızda Azure hesabınızın açık olması gerekir.
> Lütfen terminalde şu komutu çalıştırın:
> ```powershell
> az login
> ```
> Giriş yaptıktan sonra bana haber verin, dağıtım komutunu hazırlayacağım.

## Proposed Changes

### Local Deployment

1. **Giriş**: `az login` ile yetkilendirme.
2. **Dağıtım**: `az webapp up` komutu kullanılarak projenin Azure'a yüklenmesi.
   - Komut formatı: `az webapp up --name Layersupv2 --runtime "NODE|20-lts"`

## Verification Plan

### Manual Verification
1. Dağıtım tamamlandıktan sonra terminaldeki URL'yi kontrol edin.
2. `https://layersupv2.azurewebsites.net` adresine giderek sitenin güncel halini doğrulayın.
