#============================================================================================================
#
#	Gerenciamento CGI base module
#	sauron.pl
#	---------------------------------------------------------------------------
#	2003.10.12 start
#
#============================================================================================================
package	SAURON;

use strict;
#use warnings;

require './module/thorin.pl';

#------------------------------------------------------------------------------------------------------------
#
#	Module constructor - new
#	-------------------------------------------------------------------------------------
#	Argu mento：sem
#	Valor de retorno：module object
#
#------------------------------------------------------------------------------------------------------------
sub new
{
	my $this = shift;
	my ($obj, @MnuStr, @MnuUrl);
	
	$obj = {
		'SYS'		=> undef,														# MELKOR retenção
		'FORM'		=> undef,														# SAMWISE retenção
		'INN'		=> undef,														# THORIN retenção
		'MNUSTR'	=> \@MnuStr,													# Função list coluna de caracteres
		'MNUURL'	=> \@MnuUrl,													# Função list URL
		'MNUNUM'	=> 0															# Função list número
	};
	bless $obj, $this;
	
	return $obj;
}

#------------------------------------------------------------------------------------------------------------
#
#	Object geração - Create
#	-------------------------------------------------------------------------------------
#	Argu mento：$M : MELKOR module
#			$S : SAMWISE module
#	Valor de retorno：THORIN module
#
#------------------------------------------------------------------------------------------------------------
sub Create
{
	my $this = shift;
	my ($Sys, $Form) = @_;
	
	$this->{'SYS'}		= $Sys;
	$this->{'FORM'}		= $Form;
	$this->{'INN'}		= THORIN->new;
	$this->{'MNUNUM'}	= 0;
	
	return $this->{'INN'};
}

#------------------------------------------------------------------------------------------------------------
#
#	Configurações de menu - SetMenu
#	-------------------------------------------------------------------------------------
#	Argu mento：$str : exibição coluna de caracteres
#			$url : jump URL
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub SetMenu
{
	my $this = shift;
	my ($str, $url) = @_;
	
	push @{$this->{'MNUSTR'}}, $str;
	push @{$this->{'MNUURL'}}, $url;
	
	$this->{'MNUNUM'} ++;
}

#------------------------------------------------------------------------------------------------------------
#
#	Page saída - Print
#	-------------------------------------------------------------------------------------
#	Argu mento：$ttl : page title
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub Print
{
	my $this = shift;
	my ($ttl, $mode) = @_;
	my ($Tad, $Tin, $TPlus);
	
	$Tad	= THORIN->new;
	$Tin	= $this->{'INN'};
	
	PrintHTML($Tad, $ttl);																# HTML header saída
	PrintCSS($Tad, $this->{'SYS'});														# CSS saída
	PrintHead($Tad, $ttl, $mode);														# header saída
	PrintList($Tad, $this->{'MNUNUM'}, $this->{'MNUSTR'}, $this->{'MNUURL'});			# Função list saída
	PrintInner($Tad, $Tin, $ttl);														# Função conteúdo saída
	PrintCommonInfo($Tad, $this->{'FORM'});
	PrintFoot($Tad, $this->{'FORM'}->Get('UserName'), $this->{'SYS'}->Get('VERSION'),
						$this->{'SYS'}->Get('ADMIN')->{'NEWRELEASE'}->Get('Update'));	# Footer saída
	
	$Tad->Flush(0, 0, '');																# Tela saída
}

#------------------------------------------------------------------------------------------------------------
#
#	Page saída(menu list sem) - PrintNoList
#	-------------------------------------------------------------------------------------
#	Argu mento：$ttl : page title
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintNoList
{
	my $this = shift;
	my ($ttl, $mode) = @_;
	my ($Tad, $Tin);
	
	$Tad = THORIN->new;
	$Tin = $this->{'INN'};
	
	PrintHTML($Tad, $ttl);															# HTML header saída
	PrintCSS($Tad, $this->{'SYS'}, $ttl);											# CSS saída
	PrintHead($Tad, $ttl, $mode);													# Header saída
	PrintInner($Tad, $Tin, $ttl);													# Função conteúdo saída
	PrintFoot($Tad, 'NONE', $this->{'SYS'}->Get('VERSION'));						# Footer saída
	
	$Tad->Flush(0, 0, '');															# Tela saída
}

#------------------------------------------------------------------------------------------------------------
#
#	HTML header saída - PrintHTML
#	-------------------------------------------
#	Argu mento：$T   : THORIN module
#			$ttl : page title
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintHTML
{
	my ($Page, $ttl) = @_;
	
	$Page->Print("Content-type: text/html\n\n");
	$Page->Print(<<HTML);
<!DOCTYPE html>
<html lang="pt">
<head>
 
 <title>mokoichannel gerenciamento - [ $ttl ]</title>
 
HTML
	
}

#------------------------------------------------------------------------------------------------------------
#
#	Stylesheet saída - PrintCSS
#	-------------------------------------------
#	Argu mento：$Page   : THORIN module
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintCSS
{
	my ($Page, $Sys, $ttl) = @_;
	my ($data);
	
	$data = $Sys->Get('DATA');
	
$Page->Print(<<HTML);
 <meta http-equiv=Content-Type content="text/html;charset=UTF-8">
 
 <meta http-equiv="Content-Script-Type" content="text/javascript">
 <meta http-equiv="Content-Style-Type" content="text/css">
 
 <meta name="robots" content="noindex,nofollow">
 
 <link rel="stylesheet" href=".$data/admin.css" type="text/css">
 <script language="javascript" src=".$data/admin.js"></script>
 
</head>
<!--nobanner-->
HTML
	
}

#------------------------------------------------------------------------------------------------------------
#
#	Page header saída - PrintHead
#	-------------------------------------------
#	Argu mento：$Page   : THORIN module
#			$ttl : page title
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintHead
{
	my ($Page, $ttl, $mode) = @_;
	my ($common);
	
	$common = '<a href="javascript:DoSubmit';
	
$Page->Print(<<HTML);
<body>

<form name="ADMIN" action="./admin.cgi" method="POST"@{[$mode ? ' onsubmit="return Submitted();"' : '']}>

<div class="MainMenu" align="right">
HTML
	
	# System gerenciamento menu
	if ($mode == 1) {
		
$Page->Print(<<HTML);
 <a href="javascript:DoSubmit('sys.top','DISP','NOTICE');">Top</a> |
 <a href="javascript:DoSubmit('sys.bbs','DISP','LIST');">Keijiban</a> |
 <a href="javascript:DoSubmit('sys.user','DISP','LIST');">User</a> |
 <a href="javascript:DoSubmit('sys.cap','DISP','LIST');">Cap</a> |
 <a href="javascript:DoSubmit('sys.capg','DISP','LIST');">Comum Cap Group</a> |
 <a href="javascript:DoSubmit('sys.setting','DISP','INFO');">System Configuração</a> |
 <a href="javascript:DoSubmit('sys.edit','DISP','BANNER_PC');">Cada tipo edição</a> |
HTML
		
	}
	# Keijiban gerenciamento menu
	elsif ($mode == 2) {
		
$Page->Print(<<HTML);
 <a href="javascript:DoSubmit('bbs.thread','DISP','LIST');">Thread</a> |
 <a href="javascript:DoSubmit('bbs.pool','DISP','LIST');">Pool</a> |
 <a href="javascript:DoSubmit('bbs.kako','DISP','LIST');">Kako Log</a> |
 <a href="javascript:DoSubmit('bbs.setting','DISP','SETINFO');">Keijiban Configuração</a> |
 <a href="javascript:DoSubmit('bbs.edit','DISP','HEAD');">Cada Tipo Edição</a> |
 <a href="javascript:DoSubmit('bbs.user','DISP','LIST');">Gerenciamento Group</a> |
 <a href="javascript:DoSubmit('bbs.cap','DISP','LIST');">Cap Group</a> |
 <a href="javascript:DoSubmit('bbs.log','DISP','INFO');">Log Navegação</a> |
HTML
		
	}
	# Thread gerenciamento menu
	elsif ($mode == 3) {
		
$Page->Print(<<HTML);
 <a href="javascript:DoSubmit('thread.res','DISP','LIST');">Resu Lista</a> |
 <a href="javascript:DoSubmit('thread.del','DISP','LIST');">Apagação Resu Lista</a> |
HTML
		
	}
	
$Page->Print(<<HTML);
 <a href="javascript:DoSubmit('login','','');">Logoff</a>
</div>
 
<div class="MainHead" align="right">2-ch BBS System Manager</div>

<table cellspacing="0" width="100%" height="400">
 <tr>
HTML
	
}

#------------------------------------------------------------------------------------------------------------
#
#	Função list saída - PrintList
#	-------------------------------------------
#	Argu mento：$Page   : THORIN module
#			$str : Função title arranjo
#			$url : Função URL arranjo
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintList
{
	my ($Page, $n, $str, $url) = @_;
	my ($i, $strURL, $strTXT);
	
$Page->Print(<<HTML);
  <td valign="top" class="Content">
  <table width="95%" cellspacing="0">
   <tr>
    <td class="FunctionList">
HTML
	
	for ($i = 0 ; $i < $n ; $i++) {
		$strURL = $$url[$i];
		$strTXT = $$str[$i];
		if ($strURL eq '') {
			$Page->Print("    <font color=\"gray\">$strTXT</font>\n");
			if ($strTXT ne '<hr>') {
				$Page->Print('    <br>'."\n");
			}
		}
		else {
			$Page->Print("    <a href=\"javascript:DoSubmit($$url[$i]);\">");
			$Page->Print("$$str[$i]</a><br>\n");
		}
	}
	
$Page->Print(<<HTML);
    </td>
   </tr>
  </table>
  </td>
HTML
	
}

#------------------------------------------------------------------------------------------------------------
#
#	Função conteúdo saída - PrintInner
#	-------------------------------------------
#	Argu mento：$Page1 : THORIN module(MAIN)
#			$Page2 : THORIN module(conteúdo)
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintInner
{
	my ($Page1, $Page2, $ttl) = @_;
	
$Page1->Print(<<HTML);
  <td width="80%" valign="top" class="Function">
  <div class="FuncTitle">$ttl</div>
HTML
	
	$Page1->Merge($Page2);
	
	$Page1->Print("  </td>\n");
	
}

#------------------------------------------------------------------------------------------------------------
#
#	Informação comum saída - PrintCommonInfo
#	-------------------------------------------
#	Argu mento：$Sys   : 
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintCommonInfo
{
	my ($Page, $Form) = @_;
	
	my $user = $Form->Get('UserName', '');
	my $sid = $Form->Get('SessionID', '');
	
$Page->Print(<<HTML);
  <!-- ▼em assim lugar subterranêa fortaleza(ry -->
   <input type="hidden" name="MODULE" value="">
   <input type="hidden" name="MODE" value="">
   <input type="hidden" name="MODE_SUB" value="">
   <input type="hidden" name="UserName" value="$user">
   <input type="hidden" name="SessionID" value="$sid">
  <!-- △em assim lugar subterranêa fortaleza(ry -->
HTML
	
}

#------------------------------------------------------------------------------------------------------------
#
#	Footer saída - PrintFoot
#	-------------------------------------------
#	Argu mento：$Page   : THORIN module
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintFoot
{
	my ($Page, $user, $ver, $nverflag) = @_;
	
$Page->Print(<<HTML);
 </tr>
</table>

<div class="MainFoot">
 Copyright 2001 - 2013 0ch+ BBS : Loggin User - <b>$user</b><br>
 Build Version:<b>$ver</b>@{[$nverflag ? " (New Version is Available.)" : '']}
</div>

</form>

</body>
</html>
HTML
	
}

#------------------------------------------------------------------------------------------------------------
#
#	Saída da tela de finalização
#	-------------------------------------------------------------------------------------
#	@param	$processName	Nome do processo
#	@param	$pLog	Processo log
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintComplete
{
	my $this = shift;
	my ($processName, $pLog) = @_;
	my ($Page, $text);
	
	$Page = $this->{'INN'};
	
$Page->Print(<<HTML);
  <table border="0" cellspacing="0" cellpadding="0" width="100%" align="center">
   <tr>
    <td>
    
    <div class="oExcuted">
     $processName corretamente finalizou.
    </div>
   
    <div class="LogExport">Processo log</div>
    <hr>
    <blockquote class="LogExport">
HTML
	
	# Log exibição
	foreach $text (@$pLog) {
		$Page->Print("     $text<br>\n");
	}
	
$Page->Print(<<HTML);
    </blockquote>
    <hr>
    </td>
   </tr>
  </table>
HTML
	
}

#------------------------------------------------------------------------------------------------------------
#
#	Exibição de error
#	-------------------------------------------------------------------------------------
#	@param	$pLog	log用
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintError
{
	my $this = shift;
	my ($pLog) = @_;
	my ($Page, $ecode);
	
	$Page = $this->{'INN'};
	
	# Extração de error code
	$ecode = pop @$pLog;
	
$Page->Print(<<HTML);
  <table border="0" cellspacing="0" cellpadding="0" width="100%" align="center">
   <tr>
    <td>
    
    <div class="xExcuted">
HTML
	
	if ($ecode == 1000) {
		$Page->Print("     ERROR:$ecode - Não há permissão para executar o processamento desta função.\n");
	}
	elsif ($ecode == 1001) {
		$Page->Print("     ERROR:$ecode - Os itens de entrada necessários estão em branco.\n");
	}
	elsif ($ecode == 1002) {
		$Page->Print("     ERROR:$ecode - Está sendo usado caracteres fora de estipulação em item de configurações.\n");
	}
	elsif ($ecode == 2000) {
		$Page->Print("     ERROR:$ecode - Falhou em criação em keijiban directory.<br>\n");
		$Page->Print("     Permission, ou keijiban com o mesmo nome já não foi criado ka verifique, por favor.\n");
	}
	elsif ($ecode == 2001) {
		$Page->Print("     ERROR:$ecode - Falhou em geração de SETTING.TXT.\n");
	}
	elsif ($ecode == 2002) {
		$Page->Print("     ERROR:$ecode - Falhou em geração de elemento de composição de keijiban.\n");
	}
	elsif ($ecode == 2003) {
		$Page->Print("     ERROR:$ecode - Falhou em geração de informação inicial de kako log.\n");
	}
	elsif ($ecode == 2004) {
		$Page->Print("     ERROR:$ecode - Falhou em atualização de keijiban informação.\n");
	}
	else {
		$Page->Print("     ERROR:$ecode - Erro desconhecido ocorreu.\n");
	}
	
$Page->Print(<<HTML);
    </div>
    
HTML

	# Se tiver error log fazer saída
	if (@$pLog) {
		$Page->Print('<hr>');
		$Page->Print("    <blockquote>");
		foreach (@$pLog) {
			$Page->Print("    $_<br>\n");
		}
		$Page->Print("    </blockquote>");
		$Page->Print('<hr>');
	}
	
$Page->Print(<<HTML);
    </td>
   </tr>
  </table>
HTML
	
}

#============================================================================================================
#	Module terminação
#============================================================================================================
1;
