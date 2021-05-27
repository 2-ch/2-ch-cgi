#!/usr/bin/perl
#============================================================================================================
#
#	Administração system CGI
#
#============================================================================================================

use lib './perllib';

use strict;
#use warnings;
no warnings 'once';
##use CGI::Carp qw(fatalsToBrowser warningsToBrowser);


# Usar resultado de execução CGI como fim code 
exit(AdminCGI());

#------------------------------------------------------------------------------------------------------------
#
#	admin.cgi main
#	-------------------------------------------------------------------------------------
#	@param	sem
#	@return	error número
#
#------------------------------------------------------------------------------------------------------------
sub AdminCGI
{
	require './module/constant.pl';
	
	# System inicialização configuração
	my $CGI = {};
	SystemSetting($CGI);
	
	# Aquisição de informações de 0ch system
	require "./module/melkor.pl";
	my $Sys = MELKOR->new;
	$Sys->Init();
	$Sys->Set('BBS', '');
	$CGI->{'LOGGER'}->Open('.'.$Sys->Get('INFO').'/AdminLog', 100, 2 | 4);
	$CGI->{'SECINFO'}->Init($Sys);
	
	# Sonho está expandingu
	$Sys->Set('ADMIN', $CGI);
	$Sys->Set('MainCGI', $CGI);
	
	# Aquisição de informação de form
	require "./module/samwise.pl";
	my $Form = SAMWISE->new(0);
	$Form->DecodeForm(0);
	$Form->Set('FALSE', 0);
	
	# Login user configuração
	my $name = $Form->Get('UserName', '');
	my $pass = $Form->Get('PassWord', '');
	my $sid = $Form->Get('SessionID', '');
	$Form->Set('PassWord', '');
	#$Form->Set('SessionID', '');
	my ($userID, $SID) = $CGI->{'SECINFO'}->IsLogin($name, $pass, $sid);
	$CGI->{'USER'} = $userID;
	$Form->Set('SessionID', $SID);
	
	# Version check
	my $upcheck = $Sys->Get('UPCHECK', 1) - 0;
	$CGI->{'NEWRELEASE'}->Init($Sys);
	if ($upcheck) {
		$CGI->{'NEWRELEASE'}->Set('Interval', 24*60*60*$upcheck);
		$CGI->{'NEWRELEASE'}->Check;
	}
	
	# Módulo de processamento object geração
	my $modName = $Form->Get('MODULE', 'login');
	$modName = 'login' if (!$userID);
	require "./mordor/$modName.pl";
	my $oModule = MODULE->new;
	
	# Modo de exibição
	if ($Form->Get('MODE', '') eq 'DISP') {
		$oModule->DoPrint($Sys, $Form, $CGI);
	}
	# Modo de função
	elsif ($Form->Get('MODE', '') eq 'FUNC') {
		$oModule->DoFunction($Sys, $Form, $CGI);
	}
	# Login
	else {
		$CGI->{'SECINFO'}->Logout($SID);
		$oModule->DoPrint($Sys, $Form, $CGI);
	}
	
	$CGI->{'LOGGER'}->Write();
	
	return 0;
}

#------------------------------------------------------------------------------------------------------------
#
#	Administração system configuração
#	-------------------------------------------------------------------------------------
#	@param	$pSYS	referência de system administração hash
#	@return	sem
#
#------------------------------------------------------------------------------------------------------------
sub SystemSetting
{
	my ($CGI) = @_;
	
	%$CGI = (
		'SECINFO'	=> undef,		# security informação
		'LOGGER'	=> undef,		# log object
		'AD_BBS'	=> undef,		# BBS informação object
		'AD_DAT'	=> undef,		# dat informação object
		'USER'		=> undef,		# Login user ID
		'NEWRELEASE'=> undef,		# Version check
	);
	
	require './module/elves.pl';
	require './module/imrahil.pl';
	require './module/newrelease.pl';
	
	$CGI->{'SECINFO'} = ARWEN->new;
	$CGI->{'LOGGER'} = IMRAHIL->new;
	$CGI->{'NEWRELEASE'} = ZP_NEWRELEASE->new;
}

