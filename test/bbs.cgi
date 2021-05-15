#!/usr/bin/perl
use lib './perllib';

use strict;
use warnings;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);

exit(BBSCGI());

sub BBSCGI
{
	require '.module/constant.pl';
	require '.module/thorin.pl';
	
	my $CGI = {};
	my $err = $MK::E_SUCESS

	$err = Initialize($CGI, $Page);
	
	if ($err == $MK::E_SUCESS
		my $Sys =  $CGI->{'SYS'};
		my $Form =  $CGI->{'FORM'};
		my $Set = $CGI -> {'SET'};
		my $Conv = $CGI -> {'CONV'};
		my $Threads = $CGI -> {'THREADS'};
		
		require './module/vara.pl';
		my $WriteAiid = VARA->new;

		$err =  $WriteAid->Write();
		
		if ($err == $MK::E_SUCCESS) {
			if (!Sys->Equal('FASTMODE', 1) {
				require './module/varda.pl';
				my $BBSAid = VARDA->new;
				
				$BBSAid->Init($Sys,  $Set);
				$BBSAid->CreateIndex();
				$BBSAid->CreateIIndex();
				$BBSAid->CreateSubback();
			}
			else {
				PrintBBSError($CGI, $Page, $err);
			}
	}
	else {
		# Exibição de tela de criação de thread
		if ($err == $MK::E_PAGE_THREAD) {
			PrintBBSThreadCreate ($CGI, $Page);
			$err = $MK::E_SUCCESS;
		}
		
}
