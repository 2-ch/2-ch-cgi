#!/usr/bin/perl
#============================================================================================================
#
#	Busca用CGI(matiagaetesumimasen)
#	search.cgi
#	-----------------------------------------------------
#	2003.11.22 star
#	2004.09.16 Mudanças devido a system modificação
#	2009.06.19 Reescrita significativa da parte HTML
#
#============================================================================================================

use strict;
#use warnings;
##use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
no warnings 'once';

BEGIN { use lib './perllib'; }

# Usar resultado de execução CGI como fim code
exit(SearchCGI());

#------------------------------------------------------------------------------------------------------------
#
#	CGI main processo - SearchCGI
#	------------------------------------------------
#	Argu　mento：sem
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub SearchCGI
{
	my ($Sys, $Page, $Form, $BBS);
	
	require './module/melkor.pl';
	require './module/thorin.pl';
	require './module/samwise.pl';
	require './module/nazguls.pl';
	$Sys	= new MELKOR;
	$Page	= new THORIN;
	$Form	= SAMWISE->new(1);
	$BBS	= new NAZGUL;
	
	$Form->DecodeForm(1);
	$Sys->Init();
	$BBS->Load($Sys);
	PrintHead($Sys, $Page, $BBS, $Form);
	
	# No caso de ter busca word é executar busca
	if ($Form->Get('WORD', '') ne '') {
		Search($Sys, $Form, $Page, $BBS);
	}
	PrintFoot($Sys, $Page);
	$Page->Flush(0, 0, '');
}

#------------------------------------------------------------------------------------------------------------
#
#	Header saída - PrintHead
#	------------------------------------------------
#	Argu　mento：sem
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintHead
{
	my ($Sys, $Page, $BBS, $Form) = @_;
	my ($pBBS, $bbs, $name, $dir, $Banner);
	my ($sMODE, $sBBS, $sKEY, $sWORD, @sTYPE, @cTYPE, $types, $BBSpath, @bbsSet, $id);
	
	my $sanitize = sub {
		$_ = shift;
		s/&/&amp;/g;
		s/</&lt;/g;
		s/>/&gt;/g;
		s/"/&#34;/g;#"
		return $_;
	};
	
	$sMODE	= &$sanitize($Form->Get('MODE', ''));
	$sBBS	= &$sanitize($Form->Get('BBS', ''));
	$sKEY	= &$sanitize($Form->Get('KEY', ''));
	$sWORD	= &$sanitize($Form->Get('WORD'));
	@sTYPE	= $Form->GetAtArray('TYPE', 0);
	
	$types = ($sTYPE[0] || 0) | ($sTYPE[1] || 0) | ($sTYPE[2] || 0);
	$cTYPE[0] = ($types & 1 ? 'checked' : '');
	$cTYPE[1] = ($types & 2 ? 'checked' : '');
	$cTYPE[2] = ($types & 4 ? 'checked' : '');
	
	$BBSpath = $Sys->Get('BBSPATH');
	
	# Leitura do banner
	require './module/denethor.pl';
	$Banner = new DENETHOR;
	$Banner->Load($Sys);

	$Page->Print("Content-type: text/html;charset=utf-8\n\n");
	$Page->Print(<<HTML);
<!DOCTYPE html>
<html lang="pt">
<head>

 <meta http-equiv=Content-Type content="text/html;charset=utf-8">
 <meta http-equiv="Content-Script-Type" content="text/css">

 <title>Busca＠2-ch</title>

 <link rel="stylesheet" type="text/css" href="./datas/search.css">

</head>
<!--nobanner-->
<body>

<table border="1" cellspacing="7" cellpadding="3" width="95%" bgcolor="#ccffcc" style="margin-bottom:1.2em;" align="center">
 <tr>
  <td>
  <font size="+1"><b>Procura＠2-ch</b></font>
  
  <div align="center" style="margin:1.2em 0;">
  <form action="./search.cgi" method="POST">
  <table border="0">
   <tr>
    <td>Procura modo</td>
    <td>
    <select name="MODE">
HTML

	if ($sMODE eq 'ALL') {
		$Page->Print(<<HTML);
     <option value="ALL" selected>Busca inteira dentro saba</option>
     <option value="BBS">Busca inteira dentro BBS especificado</option>
     <option value="THREAD">Busca inteira dentro thread especificada</option>
HTML
	}
	elsif ($sMODE eq 'BBS' || $sMODE eq '') {
		$Page->Print(<<HTML);
     <option value="ALL">Busca inteira dentro saba</option>
     <option value="BBS" selected>Busca inteira dentro BBS especificado</option>
     <option value="THREAD">Busca inteira dentro thread especificada</option>
HTML
	}
	elsif ($sMODE eq 'THREAD') {
		$Page->Print(<<HTML);
     <option value="ALL">Busca inteira dentro saba</option>
     <option value="BBS">Busca inteira dentro BBS especificado</option>
     <option value="THREAD" selected>Busca inteira dentro thread especificada</option>
HTML
	}
	$Page->Print(<<HTML);
    </select>
    </td>
   </tr>
   <tr>
    <td>Especificação BBS</td>
    <td>
    <select name="BBS">
HTML

	# Obtenção de BBS set
	$BBS->GetKeySet('ALL', '', \@bbsSet);
	
	foreach $id (@bbsSet) {
		$name = $BBS->Get('NAME', $id);
		$dir = $BBS->Get('DIR', $id);
		
		# Se no directory de ita tiver um arquivo chamado .0ch_hidden pular
		next if ( -e "$BBSpath/$dir/.0ch_hidden" && $sBBS ne $dir );
		
		if ($sBBS eq $dir) {
			$Page->Print("     <option value=\"$dir\" selected>$name</option>\n");
		}
		else {
			$Page->Print("     <option value=\"$dir\">$name</option>\n");
		}
	}
	$Page->Print(<<HTML);
    </select>
    </td>
   </tr>
   <tr>
    <td>Especificação thread key</td>
    <td>
    <input type="text" size="20" name="KEY" value="$sKEY">
    </td>
   </tr>
   <tr>
    <td>Busca word</td>
    <td><input type="text" size="40" name="WORD" value="$sWORD"></td>
   </tr>
   <tr>
    <td>Tipo de busca</td>
    <td>
    <input type="checkbox" name="TYPE" value="1" $cTYPE[0]>Nome busca<br>
    <input type="checkbox" name="TYPE" value="4" $cTYPE[2]>ID・Data busca<br>
    <input type="checkbox" name="TYPE" value="2" $cTYPE[1]>Texto busca<br>
    </td>
   </tr>
   <tr>
    <td colspan="2" align="right">
    <hr>
    <input type="submit" value="Busca" style="width:150px;">
    </td>
   </tr>
  </table>
  </form>
  </div>
  </td>
 </tr>
</table>

HTML

	$Banner->Print($Page, 95, 0, 0) if($Sys->Get('BANNER'));
}

#------------------------------------------------------------------------------------------------------------
#
#	Footer saída - PrintHead
#	------------------------------------------------
#	Argu　mento：sem
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintFoot
{
	my ($Sys, $Page) = @_;
	my ($ver, $cgipath);
	
	$ver = $Sys->Get('VERSION');
	$cgipath	= $Sys->Get('CGIPATH');
	
	$Page->Print(<<HTML);

<div class="foot">
<a href="http://2-ch.heliohost.org/">mokoichannel</a>
SEARCH.CGI - $ver
</div>

HTML
}

#------------------------------------------------------------------------------------------------------------
#
#	Resultados de busca saída - Search
#	------------------------------------------------
#	Argu　mento：sem
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub Search
{
	my ($Sys, $Form, $Page, $BBS) = @_;;
	my ($Search, $Mode, $Result, @elem, $n, $base, $word);
	my (@types, $Type);
	
	require './module/balrogs.pl';
	$Search = new BALROGS;
	
	$Mode = 0 if ($Form->Equal('MODE', 'ALL'));
	$Mode = 1 if ($Form->Equal('MODE', 'BBS'));
	$Mode = 2 if ($Form->Equal('MODE', 'THREAD'));
	
	@types = $Form->GetAtArray('TYPE', 0);
	$Type = ($types[0] || 0) | ($types[1] || 0) | ($types[2] || 0);
	
	my $sanitize = sub {
		$_ = shift;
		s/&/&amp;/g;
		s/</&lt;/g;
		s/>/&gt;/g;
		return $_;
	};
	
	# Configuração busca object e execução da busca
	$Search->Create($Sys, $Mode, $Type, $Form->Get('BBS', ''), $Form->Get('KEY', ''));
	$Search->Run(&$sanitize($Form->Get('WORD')));
	
	if ($@ ne '') {
		PrintSystemError($Page, $@);
		return;
	}
	
	# Resultados de busca set obtenção
	$Result = $Search->GetResultSet();
	$n		= $Result ? @$Result : 0;
	$base	= $Sys->Get('BBSPATH');
	$word	= $Form->Get('WORD');
	
	PrintResultHead($Page, $n);
	
	# Busca hit tem acima de 1 sujeito
	if ($n > 0) {
		require './module/galadriel.pl';
		my $Conv = new GALADRIEL;
		$n = 1;
		foreach (@$Result) {
			@elem = split(/<>/);
			PrintResult($Page, $BBS, $Conv, $n, $base, \@elem);
			$n++;
		}
	}
	# Busca hit sem
	else {
		PrintNoHit($Page);
	}
	
	PrintResultFoot($Page);
}

#------------------------------------------------------------------------------------------------------------
#
#	Resultados de busca header saída - PrintResultHead
#	------------------------------------------------
#	Argu　mento：Page : saída module
#	Valor de retorno：sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintResultHead
{
	my ($Page, $n) = @_;
	
	$Page->Print(<<HTML);
<table border="1" cellspacing="7" cellpadding="3" width="95%" bgcolor="#efefef" style="margin-bottom:1.2em;" align="center">
 <tr>
  <td>
  <div class="hit" style="margin-top:1.2em;">
   <b>
   【Hit número：$n】
   <font size="+2" color="red">Resultados de busca</font>
   </b>
  </div>
  <dl>
HTML
}

#------------------------------------------------------------------------------------------------------------
#
#	Resultados de busca conteúdo saída
#	-------------------------------------------------------------------------------------
#	@param	$Page	THORIN
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintResult
{
	my ($Page, $BBS, $Conv, $n, $base, $pResult) = @_;
	my ($name, @bbsSet);
	
	$BBS->GetKeySet('DIR', $$pResult[0], \@bbsSet);
	
	if (@bbsSet > 0) {
		$name = $BBS->Get('NAME', $bbsSet[0]);
		
		$Page->Print("   <dt>$n Nome：<b>");
		if ($$pResult[4] eq '') {
			$Page->Print("<font color=\"green\">$$pResult[3]</font>");
		}
		else {
			$Page->Print("<a href=\"mailto:$$pResult[4]\">$$pResult[3]</a>");
		}
		
	$Page->Print(<<HTML);
 </b>：$$pResult[5]</dt>
    <dd>
    $$pResult[6]
    <br>
    <hr>
    <a target="_blank" href="$base/$$pResult[0]/">【$name】</a>
    <a target="_blank" href="./read.cgi/$$pResult[0]/$$pResult[1]/">【Thread】</a>
    <a target="_blank" href="./read.cgi/$$pResult[0]/$$pResult[1]/$$pResult[2]">【Resu】</a>
    <br>
    <br>
    </dd>
    
HTML
	}
}

#------------------------------------------------------------------------------------------------------------
#
#	Resultados de busca footer saída
#	-------------------------------------------------------------------------------------
#	@param	$Page	THORIN
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintResultFoot
{
	my ($Page) = @_;
	
	$Page->Print("  </dl>\n  </td>\n </tr>\n</table>\n");
}

#------------------------------------------------------------------------------------------------------------
#
#	NoHit saída
#	-------------------------------------------------------------------------------------
#	@param	$Page	THORIN
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintNoHit
{
	my ($Page) = @_;
	
	$Page->Print(<<HTML);
<dt>
 0 Nome：<font color="forestgreen"><b>Pesquisa engine\＠2-ch</b></font>：No Hit
</dt>
<dd>
 <br>
 <br>
 ＿|￣|○　nem um hit foi feito。。<br>
 <br>
</dd>
HTML
}

#------------------------------------------------------------------------------------------------------------
#
#	System error saída
#	-------------------------------------------------------------------------------------
#	@param	$Page	THORIN
#	@param	$msg	error message
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintSystemError
{
	my ($Page, $msg) = @_;
	
	$Page->Print(<<HTML);
<br>
<table border="1" cellspacing="7" cellpadding="3" width="95%" bgcolor="#efefef" align="center">
 <tr>
  <td>
  <dl>
  <div class="title">
  <small><b>【Hit número：0】</b></small><font size="+2" color="red">System error</font>
  </div>
   <dt>0 Nome：<font color="forestgreen"><b>Pesquisa engine\＠2-ch</b></font>：System error</dt>
    <dd>
    <br>
    <br>
    $msg<br>
    <br>
    <br>
    </dd>
  </dl>
  </td>
 </tr>
</table>
HTML
}
