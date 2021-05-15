#!/usr/bin/perl
use strict;
use warnings;
use CGI::Carp qw(fatalsToBrowser warningsToBrowser);

exit(AdminCGI());

sub AdminCGI
{
	require './module/constant.pl';
	
	my $CGI = {};
	