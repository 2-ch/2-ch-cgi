#!/usr/bin/perl
#============================================================================================================
#
#	index atualização用CGI
#	remake.cgi
#	-------------------------------------------------------------------------------------
#	2006.08.05 extraido apenas partes necessárias do bbs.cgi
#
#============================================================================================================

use strict;
#use warnings;
##use CGI::Carp qw(fatalsToBrowser warningsToBrowser);
no warnings 'once';

BEGIN { use lib './perllib'; }

# Usar resultado de execução CGI como fim code 
exit(REMAKECGI());
#------------------------------------------------------------------------------------------------------------
#
#	remake.cgi main
#	-------------------------------------------------------------------------------------
#	@param	sem
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub REMAKECGI
{
	my (%SYS, $Page, $err);
	
	require './module/constant.pl';
	
	require './module/thorin.pl';
	$Page = new THORIN;
	
	# Se sucedir na inicialização começar processo de atualização
	if (($err = Initialize(\%SYS, $Page)) == 0) {
		#require './module/baggins.pl';
		require './module/varda.pl';
		#my $Threads = BILBO->new;
		my $BBSAid = new VARDA;
		my $Sys = $SYS{'SYS'};
		
		# subject.txt
		#$Threads->Load($Sys);
		#$Threads->UpdateAll($Sys);
		#$Threads->Save($Sys);
		
		# index.html
		$BBSAid->Init($Sys, $SYS{'SET'});
		$BBSAid->CreateIndex();
		$BBSAid->CreateIIndex();
		$BBSAid->CreateSubback();
		
		PrintBBSJump(\%SYS, $Page);
	}
	else {
		PrintBBSError(\%SYS, $Page, $err);
	}
	
	# exibição do resultado
	$Page->Flush('', 0, 0);
	
	return $err;
}

#------------------------------------------------------------------------------------------------------------
#
#	remake.cgi inicialização
#	-------------------------------------------------------------------------------------
#	@param	sem
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub Initialize
{
	my ($Sys, $Page) = @_;
	my ($bbs);
	
	# Inicialização dos módulos em uso
	require './module/melkor.pl';
	require './module/isildur.pl';
	require './module/radagast.pl';
	require './module/galadriel.pl';
	require './module/samwise.pl';
	
	%$Sys = (
		'SYS'		=> new MELKOR,
		'SET'		=> new ISILDUR,
		'COOKIE'	=> new RADAGAST,
		'CONV'		=> new GALADRIEL,
		'FORM'		=> SAMWISE->new(1),
		'PAGE'		=> $Page,
	);
	
	# form informação configuração
	$Sys->{'FORM'}->DecodeForm(1);
	
	# system informação configuração
	if ($Sys->{'SYS'}->Init()) {
		return 990;
	}
	
	# Sonho está expandingu
	$Sys->{'SYS'}->{'MainCGI'} = $Sys;
	
	$bbs = $Sys->{'FORM'}->Get('bbs', '');
	$Sys->{'SYS'}->Set('BBS', $bbs);
	$Sys->{'SYS'}->Set('BBSPATH_ABS', $Sys->{'CONV'}->MakePath($Sys->{'SYS'}->Get('CGIPATH'), $Sys->{'SYS'}->Get('BBSPATH')));
	$Sys->{'SYS'}->Set('BBS_ABS', $Sys->{'CONV'}->MakePath($Sys->{'SYS'}->Get('BBSPATH_ABS'), $Sys->{'SYS'}->Get('BBS')));
	$Sys->{'SYS'}->Set('BBS_REL', $Sys->{'CONV'}->MakePath($Sys->{'SYS'}->Get('BBSPATH'), $Sys->{'SYS'}->Get('BBS')));
	
	if ($bbs eq '' || $bbs =~ /[^A-Za-z0-9_\-\.]/ || ! -d $Sys->{'SYS'}->Get('BBS_REL')) {
		return 999;
	}
	
	$Sys->{'SYS'}->Set('CLIENT', $Sys->{'CONV'}->GetClient());
	$Sys->{'SYS'}->Set('AGENT', $Sys->{'CONV'}->GetAgentMode($Sys->{'SYS'}->Get('CLIENT')));
	$Sys->{'SYS'}->Set('MODE', 'CREATE');
	
	# SETTING.TXT leitura
	if (! $Sys->{'SET'}->Load($Sys->{'SYS'})) {
		return 999;
	}
	
	return 0;
}


#------------------------------------------------------------------------------------------------------------
#
#	remake.cgi jump page exibição
#	-------------------------------------------------------------------------------------
#	@param	sem
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintBBSJump
{
	my ($Sys, $Page) = @_;
	my ($SYS, $bbsPath);
	
	$SYS		= $Sys->{'SYS'};
	$bbsPath	= $SYS->Get('BBS_REL');
	
	# keitai用 exibição
	if ($SYS->Get('CLIENT') & $ZP::C_MOBILEBROWSER) {
		$Page->Print("Content-type: text/html\n\n");
		$Page->Print('<!--nobanner--><html><body>index wo atualizou。<br>');
		$Page->Print("<a href=\"$bbsPath/i/\">de aqui</a>");
		$Page->Print("ao keijiban voltekudasai。\n");
	}
	# PC用 exibição
	else {
		my $oSET = $Sys->{'SET'};
		
		$Page->Print("Content-type: text/html\n\n<html><head><title>");
		$Page->Print('index wo atualizou。</title><!--nobanner-->');
		$Page->Print('<meta http-equiv="Content-Type" content="text/html; ');
		$Page->Print("charset=UTF8\"><meta content=0;URL=$bbsPath/ ");
		$Page->Print('http-equiv=refresh></head><body>index wo atualizou。');
		$Page->Print('<br><br>Até a tela mudar um tempo esperekudasai。');
		$Page->Print('<br><br><br><br><br><hr>');
		
	}
	# coluna de notificação exibição (caso não querer exibição é comment out ou condição a 0)
	if (0) {
		require './module/denethor.pl';
		my $BANNER = new DENETHOR;
		$BANNER->Load($SYS);
		$BANNER->Print($Page, 100, 0, $SYS->Get('AGENT'));
	}
	$Page->Print('</body></html>');
}

#------------------------------------------------------------------------------------------------------------
#
#	remake.cgi error page exibição
#	-------------------------------------------------------------------------------------
#	@param	sem
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub PrintBBSError
{
	my ($Sys, $Page, $err) = @_;
	my ($ERROR);
	
	require './module/orald.pl';
	$ERROR = new ORALD;
	$ERROR->Load($Sys->{'SYS'});
	
	$ERROR->Print($Sys, $Page, $err, $Sys->{'SYS'}->Get('AGENT'));
}

