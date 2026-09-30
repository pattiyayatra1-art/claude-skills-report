# Match the user's model report styling after build_research_docx.ps1:
#  navy table header with white bold text, light-blue banded rows, bold table/figure captions,
#  Heading 3 flush left. Then refresh TOC fields and export PDF.
param([string]$Docx, [string]$Pdf)
$ErrorActionPreference = "Stop"
$NAVY = 0x64381F      # RGB 1F3864 as Word BGR
$BAND = 0xF2E6DC      # RGB DCE6F2
$word = $null; $doc = $null
try {
    $word = New-Object -ComObject Word.Application
    $word.Visible = $false; $word.DisplayAlerts = 0
    $doc = $word.Documents.Open($Docx)
    foreach ($t in $doc.Tables) {
        $t.Borders.Enable = 1
        for ($r = 1; $r -le $t.Rows.Count; $r++) {
            $row = $t.Rows.Item($r)
            if ($r -eq 1) {
                $row.Shading.BackgroundPatternColor = $NAVY
                $row.Range.Font.Color = 0xFFFFFF; $row.Range.Font.Bold = 1; $row.Range.Font.BoldBi = 1
            } elseif ($r % 2 -eq 1) {
                $row.Shading.BackgroundPatternColor = $BAND
            }
        }
    }
    foreach ($name in @("TH Table Caption", "TH Figure Caption")) {
        $f = $doc.Styles.Item($name).Font; $f.Bold = 1; $f.BoldBi = 1
    }
    $h3 = $doc.Styles.Item(-4).ParagraphFormat; $h3.LeftIndent = [single]0
    # model puts สารบัญตาราง and สารบัญภาพ on one page: the last front heading must not break the page
    $front = @($doc.Paragraphs | Where-Object { $_.Style.NameLocal -eq "TH Front Heading" })
    if ($front.Count -ge 2) { $last = $front[$front.Count - 1]; $last.Format.PageBreakBefore = 0; $last.Format.SpaceBefore = [single]24 }
    foreach ($i in -2, -3, -4) { $doc.Styles.Item($i).Font.Color = 0 }
    for ($k = 0; $k -lt 2; $k++) { $doc.Repaginate(); foreach ($toc in $doc.TablesOfContents) { $toc.Update() } }
    $doc.Save()
    if ($Pdf) { $doc.SaveAs([ref]$Pdf, [ref]17) }
    Write-Output ("PAGES=" + $doc.ComputeStatistics(2))
}
finally {
    if ($doc) { $doc.Close([ref]0) }
    if ($word) { $word.Quit(); [System.Runtime.Interopservices.Marshal]::ReleaseComObject($word) | Out-Null }
    [GC]::Collect(); [GC]::WaitForPendingFinalizers()
}
