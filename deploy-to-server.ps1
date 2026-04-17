# 仓酷家部署脚本 - PowerShell版本
# 自动处理SSH密码输入

$serverIP = "150.158.45.157"
$username = "root"
$password = "Anderson2026@!"

Write-Host "==========================================" -ForegroundColor Green
Write-Host "  仓酷家服务器部署脚本" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
Write-Host ""

# 创建WScript.Shell对象用于发送按键
$wshell = New-Object -ComObject WScript.Shell

# 函数：执行SSH命令并自动输入密码
function Invoke-SSHCommand {
    param(
        [string]$Command,
        [int]$WaitSeconds = 5
    )
    
    Write-Host "执行: $Command" -ForegroundColor Yellow
    
    # 启动进程
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "ssh"
    $psi.Arguments = "-o StrictHostKeyChecking=no -o ConnectTimeout=30 $username@$serverIP `"$Command`""
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    
    $process = [System.Diagnostics.Process]::Start($psi)
    
    # 等待密码提示
    Start-Sleep -Milliseconds 500
    
    # 发送密码
    $process.StandardInput.WriteLine($password)
    $process.StandardInput.Flush()
    
    # 等待执行完成
    Start-Sleep -Seconds $WaitSeconds
    
    $output = $process.StandardOutput.ReadToEnd()
    $error = $process.StandardError.ReadToEnd()
    
    $process.Kill()
    
    if ($output) {
        Write-Host $output -ForegroundColor White
    }
    if ($error -and $error -notlike "*password*") {
        Write-Host $error -ForegroundColor Red
    }
    
    return $output
}

# 函数：使用SCP上传文件
function Send-SCPFile {
    param(
        [string]$LocalFile,
        [string]$RemotePath,
        [int]$WaitSeconds = 3
    )
    
    Write-Host "上传: $LocalFile -> $RemotePath" -ForegroundColor Yellow
    
    $psi = New-Object System.Diagnostics.ProcessStartInfo
    $psi.FileName = "scp"
    $psi.Arguments = "-o StrictHostKeyChecking=no $LocalFile $username@$serverIP`:$RemotePath"
    $psi.RedirectStandardInput = $true
    $psi.RedirectStandardOutput = $true
    $psi.RedirectStandardError = $true
    $psi.UseShellExecute = $false
    $psi.CreateNoWindow = $true
    
    $process = [System.Diagnostics.Process]::Start($psi)
    
    Start-Sleep -Milliseconds 500
    $process.StandardInput.WriteLine($password)
    $process.StandardInput.Flush()
    
    Start-Sleep -Seconds $WaitSeconds
    
    $output = $process.StandardOutput.ReadToEnd()
    $error = $process.StandardError.ReadToEnd()
    
    $process.Kill()
    
    if ($output) { Write-Host $output }
    if ($error -and $error -notlike "*password*" -and $error -notlike "*100%*") {
        Write-Host $error -ForegroundColor Red
    }
}

# ===== 开始部署 =====

# 1. 检查服务器连接
Write-Host "[1/5] 检查服务器连接..." -ForegroundColor Cyan
Invoke-SSHCommand "echo '服务器连接成功' && uname -a" 3

# 2. 上传部署脚本
Write-Host "`n[2/5] 上传部署脚本..." -ForegroundColor Cyan
Send-SCPFile "server-setup.sh" "/tmp/server-setup.sh" 3

# 3. 执行部署脚本
Write-Host "`n[3/5] 执行服务器环境配置..." -ForegroundColor Cyan
Invoke-SSHCommand "chmod +x /tmp/server-setup.sh && /tmp/server-setup.sh" 60

# 4. 检查部署结果
Write-Host "`n[4/5] 检查部署结果..." -ForegroundColor Cyan
Invoke-SSHCommand "ls -la /var/www/cangkujia/ && df -h && free -h" 3

# 5. 检查Nginx状态
Write-Host "`n[5/5] 检查Nginx状态..." -ForegroundColor Cyan
Invoke-SSHCommand "systemctl status nginx --no-pager | head -20" 3

Write-Host "`n==========================================" -ForegroundColor Green
Write-Host "  部署脚本执行完成！" -ForegroundColor Green
Write-Host "==========================================" -ForegroundColor Green
