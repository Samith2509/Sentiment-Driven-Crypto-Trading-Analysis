$sentiment = Import-Csv "sentiment.csv"
$hashSentiment = @{}
foreach ($s in $sentiment) {
    $hashSentiment[$s.date] = $s.classification
}

$fearWin = 0; $fearTotal = 0; $fearPnL = 0.0; $fearSize = 0.0
$greedWin = 0; $greedTotal = 0; $greedPnL = 0.0; $greedSize = 0.0
$fearShort = 0; $fearLong = 0; $greedShort = 0; $greedLong = 0

$trades = Import-Csv "trades.csv"
foreach ($t in $trades) {
    # Convert 'Timestamp IST' like "02-12-2024 22:50" -> '2024-12-02'
    $ist = $t.'Timestamp IST'
    if ([string]::IsNullOrWhiteSpace($ist)) { continue }
    $splitSpace = $ist.Split(" ")
    if ($splitSpace.Length -eq 0) { continue }
    $parts = $splitSpace[0].Split("-")
    if ($parts.Length -eq 3) {
        $dd = $parts[0]
        $mm = $parts[1]
        $yyyy = $parts[2]
        $dateStr = "$yyyy-$mm-$dd"
        
        $class = $hashSentiment[$dateStr]
        if ($class -eq $null) { continue }
        
        $pnlStr = $t.'Closed PnL'
        $pnl = 0.0
        if ([double]::TryParse($pnlStr, [ref]$pnl)) {
        }
        $isWin = ($pnl -gt 0)

        $sizeStr = $t.'Size USD'
        $size = 0.0
        if ([double]::TryParse($sizeStr, [ref]$size)) {
        }
        
        $isLong = ($t.Side -eq 'BUY')
        $isShort = ($t.Side -eq 'SELL')

        if ($class -match 'Fear') {
            $fearTotal++
            if ($isWin) { $fearWin++ }
            $fearPnL += $pnl
            $fearSize += $size
            if ($isLong) { $fearLong++ }
            if ($isShort) { $fearShort++ }
        } elseif ($class -match 'Greed') {
            $greedTotal++
            if ($isWin) { $greedWin++ }
            $greedPnL += $pnl
            $greedSize += $size
            if ($isLong) { $greedLong++ }
            if ($isShort) { $greedShort++ }
        }
    }
}

Write-Output "--- RESULTS ---"
Write-Output "Fear Total: $fearTotal, Fear Win: $fearWin, Fear PnL: $fearPnL, Fear Size: $fearSize"
Write-Output "Fear Long: $fearLong, Fear Short: $fearShort"
Write-Output "Greed Total: $greedTotal, Greed Win: $greedWin, Greed PnL: $greedPnL, Greed Size: $greedSize"
Write-Output "Greed Long: $greedLong, Greed Short: $greedShort"

