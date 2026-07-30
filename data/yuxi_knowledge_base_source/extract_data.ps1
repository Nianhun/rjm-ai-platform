Write-Host 'Reading NDJSON...'
$productList = New-Object System.Collections.Generic.List[System.Object]
$reader = [System.IO.StreamReader]::new('products.ndjson')
$lineNum = 0
while (($line = $reader.ReadLine()) -ne $null) {
    $lineNum++
    try {
        $productList.Add(($line | ConvertFrom-Json))
    } catch {}
}
$reader.Close()
Write-Host ('Products: ' + $productList.Count)

$ingredientsCount = 0
$ingredientNames = New-Object System.Collections.Generic.List[System.String]
foreach ($p in $productList) {
    if ($p.ingredients) {
        foreach ($ing in $p.ingredients) {
            $ingredientsCount++
            $ingredientNames.Add($ing.ingredient_name)
        }
    }
}
$unique = $ingredientNames | Sort-Object -Unique
Write-Host ('Ingredient entries: ' + $ingredientsCount)
Write-Host ('Unique ingredients: ' + $unique.Count)

$ingredientsCsv = Import-Csv 'ingredients_full.csv'
Write-Host ('Ingredient details: ' + $ingredientsCsv.Count)

$productUrls = Get-Content 'product_urls.csv' | Select-Object -Skip 1
Write-Host ('Product URLs: ' + $productUrls.Count)

$allUrls = Get-Content 'all_product_urls.csv' | Select-Object -Skip 1
Write-Host ('All product URLs: ' + $allUrls.Count)

$ingUrls = Get-Content 'ingredient_urls.csv' | Select-Object -Skip 1
Write-Host ('Ingredient URLs: ' + $ingUrls.Count)

$csvProduct = Import-Csv 'products.csv'
Write-Host ('CSV rows: ' + $csvProduct.Count)

Write-Host ''
Write-Host '=== First 5 products ==='
$productList | Select-Object -First 5 | ForEach-Object { Write-Host ('  ' + $_.product_name + ' | ingr: ' + $_.ingredient_count) }

$discontinued = $productList | Where-Object { $_.is_discontinued -eq $true }
Write-Host ('Discontinued: ' + $discontinued.Count)

$top = $productList | Sort-Object ingredient_count -Descending | Select-Object -First 10
Write-Host ''
Write-Host '=== Top 10 (most ingredients) ==='
$top | ForEach-Object { Write-Host ('  ' + $_.product_name + ' | ' + $_.ingredient_count) }

$grouped = $ingredientNames | Group-Object | Sort-Object Count -Descending | Select-Object -First 20
Write-Host ''
Write-Host '=== Top 20 ingredients ==='
$grouped | ForEach-Object { Write-Host ('  ' + $_.Name + ': ' + $_.Count) }
