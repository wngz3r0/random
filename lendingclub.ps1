Function Convert-FromPercent {
	Param(
		[Parameter(Mandatory = $True)][String] $string)
	
	([int]($string -replace("%",""))) / 100
}

Function Calculate-MonthlyPayment {
	Param(
		[Parameter(Mandatory = $True)][String] $amount,
		[Parameter(Mandatory = $True)][String] $apr,
		[Parameter(Mandatory = $True)][String] $loanLength)

	$amount = [int]$amount
	$apr = Convert-FromPercent $apr
	$months = [int]$loanLength.Split(" ")[0]
	$years = $months / 12
	$totalLoanCost = (1 + $apr) * $amount * $years
	return $totalLoanCost / $months
}

Function Calculate-CreditLimit {
	Param(
		[Parameter(Mandatory = $True)][String] $creditBalance,
		[Parameter(Mandatory = $True)][String] $creditUtilization)
	
	return  [double]$creditBalance / (Convert-FromPercent $creditUtilization)
}

Function Get-DesiredLoans {
	Param(
		[Parameter(Mandatory = $True)] $csv)
	
	$csv | Where-Object {
		($_."CREDIT Rating"[0] -ge "B") -and
		($_."CREDIT Rating"[0] -le "E") -and
		([int]$_."Amount Requested" -le 25000) -and
		((Calculate-MonthlyPayment $_."Amount Requested" $_.APR $_."Loan Length") -lt ($_."Monthly Income" / 8)) -and
		((Convert-FromPercent $_."Revolving Line Utilization") -lt .65) -and
		([int]$_."Revolving CREDIT Balance" -lt 30000) -and
		((Calculate-CreditLimit $_."Revolving CREDIT Balance" $_."Revolving Line Utilization") -ge [int] $_."Amount Requested") -and
		((Convert-FromPercent $_."Debt-To-Income Ratio") -le .2) -and
		([int]$_."Inquiries in the last 6 months" -le 2) -and
		([int]$_."Accounts now Delinquent" -eq 0) -and
		([int]$_."Public Records on File" -eq 0) -and
		([int]$_."Monthly income" -lt 8000) -and
		([int]$_."Open CREDIT Lines" -ge 3)
	}
}
echo ("Please save InFundingStats.csv to " + $PWD.Path + "\InFundingStats.csv")
$ie = New-Object -ComObject InternetExplorer.Application
$ie.Navigate("http://www.lendingclub.com/info/download.action?file=InFundingStats.csv")
$ie.visible = $True
Read-Host "Press the enter key when finished"
$csv = Get-Content .\InFundingStats.csv | select -skip 1 | ConvertFrom-Csv
$data = Get-DesiredLoans $csv
$ie = New-Object -ComObject InternetExplorer.Application
$ie.Navigate("https://www.lendingclub.com/browse/loanDetail.action?loan_id=" + $data[0]."Loan ID")
$data | select -skip 1 | ForEach-Object {
	$site = "https://www.lendingclub.com/browse/loanDetail.action?loan_id=" + $_."Loan ID"
	$ie.Navigate2($site, 0x1000) 
}

echo ([String]$data.Count + " Loans Found")
Read-Host "Press the enter key to display the loans. Press ctrl-c to cancel"
$ie.visible = $True

