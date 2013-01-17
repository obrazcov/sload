#! /usr/bin/env python
print "# Python console remote interface traffic load (by SNMP)(sload.py) (26/09/2012) version 0.1.5"
print "# Coded by Yevgen Obraztsov - obrazcov@users.sf.net"
# Syntax: ./sload.py host
######

import time, sys
#sys.path.append("./pysnmp-4.2.2-py2.4.egg")
from pysnmp.entity.rfc3413.oneliner import cmdgen

p_community='public'
p_host='172.18.216.1'
p_oid='1.3.6.1.2.1.1.1.0'
p_ifInOctets_oid='.1.3.6.1.2.1.2.2.1.10.'
p_ifOutOctets_oid='.1.3.6.1.2.1.2.2.1.16.'
p_ifDescTable_oid='1.3.6.1.2.1.2.2.1.2'
def snmpGet(l_community,l_host,l_oid):
	errorIndication, errorStatus, \
					 errorIndex, varBinds = cmdgen.CommandGenerator().getCmd(
		# SNMP v2
		cmdgen.CommunityData('test-agent', l_community),
		cmdgen.UdpTransportTarget((l_host, 161)),
		# Plain OID
		l_oid
		# ((mib-name, mib-symbol), instance-id)
		# (('SNMPv2-MIB', 'sysDescr'), 0)
		)
	if errorIndication:
		print errorIndication
	else:
		if errorStatus:
			print '%s at %s\n' % (
				errorStatus.prettyPrint(),
				errorIndex and varBinds[int(errorIndex)-1] or '?'
				)
		else:
			return	varBinds[0][1]

def snmpWalk(l_community,l_host,l_oid):
	errorIndication, errorStatus, \
					 errorIndex, varBindTable = cmdgen.CommandGenerator().nextCmd(
		# SNMP v2
		cmdgen.CommunityData('test-agent', l_community),
		cmdgen.UdpTransportTarget((l_host, 161)),
		# Plain OID
		l_oid
		# ((mib-name, mib-symbol), instance-id)
		# (('SNMPv2-MIB', 'sysDescr'), 0)
		)
	if errorIndication:
		print errorIndication
	else:
		if errorStatus:
			print '%s at %s\n' % (
				errorStatus.prettyPrint(),
				errorIndex and varBinds[int(errorIndex)-1] or '?'
				)
		else:
			return	varBindTable

def main():
	p_host=''
	if len(sys.argv)<2:
		print "Usage: ./sload.py host"
		sys.exit()
	else: p_host = sys.argv[1]
	print snmpGet(p_community,p_host,p_oid)
	oldInOctets, oldOutOctets, InOctets, OutOctets = 0, 0, 0, 0
	InSpeed, OutSpeed = 0, 0
	p_ifDescTable=snmpWalk(p_community,p_host,p_ifDescTable_oid)
	p_ifDescTableDict={}
	p_ifCount2=len(p_ifDescTable)
	print 'Interface table:'
	star=''
	for p_ifDescTableRow in p_ifDescTable:
            for name, val in p_ifDescTableRow:
				idx=name.prettyPrint()[20:]
				if len(idx)==1: idx='0'+idx
				star=star+idx+' = '+val.prettyPrint()+'\t\t\t\t'
				if int(idx)<100: p_ifDescTableDict[idx]=val.prettyPrint()
				if star.count('=') == 2:
#					print star
					star=''
	p_ifCount=len(p_ifDescTableDict)
	p_ifDescTableList=sorted(p_ifDescTableDict.keys())
	i=0
	star=''
	p_ifCountHalf=int(p_ifCount/2)
	p_ifCountOdd=p_ifCount % 2
	for idx in p_ifDescTableList:
		if i < p_ifCountHalf:
			i2=i+p_ifCountHalf+p_ifCountOdd
			star='#'+p_ifDescTableList[i]+' = '+p_ifDescTableDict[p_ifDescTableList[i]]
			if len(star) % 8 : tabs='\t\t\t'
			else: tabs='\t\t'
			print star+tabs+'#'+p_ifDescTableList[i2]+' = '+p_ifDescTableDict[p_ifDescTableList[i2]]
		if i >= p_ifCountHalf and p_ifCountOdd:
			print '#'+p_ifDescTableList[i]+' = '+p_ifDescTableDict[p_ifDescTableList[i]]
			break
		i+=1
	p_ifId=str(int(raw_input("Choose interface number: \r\n")))
	print '###########################################'
	print 'IF-MIB::ifDescr.'+p_ifId+' = ',snmpGet(p_community,p_host,'.1.3.6.1.2.1.2.2.1.2.'+p_ifId)
	print 'IF-MIB::ifMtu.'+p_ifId+' = ',snmpGet(p_community,p_host,'.1.3.6.1.2.1.2.2.1.4.'+p_ifId),'Bytes'
	print 'IF-MIB::ifSpeed.'+p_ifId+' = ',str(int(snmpGet(p_community,p_host,'.1.3.6.1.2.1.2.2.1.5.'+p_ifId))/1000000)+' Mbps'
	#print 'IF-MIB::ifPhysAddress.'+p_ifId+' = ',str(snmpGet(p_community,p_host,'.1.3.6.1.2.1.2.2.1.6.'+p_ifId))
	ifStates=('','Up','Down')
	print 'IF-MIB::ifAdminStatus.'+p_ifId+' = ', ifStates[int(snmpGet(p_community,p_host,'.1.3.6.1.2.1.2.2.1.7.'+p_ifId))]
	print 'IF-MIB::ifOperStatus.'+p_ifId+' = ',ifStates[int(snmpGet(p_community,p_host,'.1.3.6.1.2.1.2.2.1.8.'+p_ifId))]
	#print 'IF-MIB::ifLastChange.'+p_ifId+' = ',snmpGet(p_community,p_host,'.1.3.6.1.2.1.2.2.1.9.'+p_ifId)
	print '###########################################'
	oldInOctets, oldOutOctets, firstInOctets, firstOutOctets, tc = -1, -1, -1, -1, 0
	oldInTime, oldOutTime, firstInTime, firstOutTime = 0, 0, 0, 0
	if len(p_ifId)==1: p_ifId2='0'+p_ifId
	else: p_ifId2=p_ifId
	while 1:
		InOctets=snmpGet(p_community,p_host,p_ifInOctets_oid+p_ifId)
		InTime=time.time()
		OutOctets=snmpGet(p_community,p_host,p_ifOutOctets_oid+p_ifId)
		OutTime=time.time()
		tc1=InTime-oldInTime
		tc2=OutTime-oldOutTime
		ftc1=InTime-firstInTime
		ftc2=OutTime-firstOutTime
		#print tc1, tc2, ftc1, ftc2
		InSpeed=(InOctets-oldInOctets)/1024/tc1*8
		OutSpeed=(OutOctets-oldOutOctets)/1024/tc2*8
		if tc1>0:
			AvgInSpeed=(InOctets-firstInOctets)/ftc1/1024*8
			AvgOutSpeed=(OutOctets-firstOutOctets)/ftc2/1024*8
		#print '\"'+p_ifDescTableDict[p_ifId2]+'\" --->'
		if oldInOctets<>-1 :
			star1='Current: In/Out  '+str(InSpeed)+'/'+str(OutSpeed)+' Kbps'
			star2='Avg: In/Out  '+str(AvgInSpeed)+'/'+str(AvgOutSpeed)+' Kbps'
			if (len(star1)+1) % 8: print star1,'\t\t\t',star2
			else: print star1,'\t\t',star2
		else:
			firstInOctets=InOctets
			firstOutOctets=OutOctets
			firstInTime=InTime
			firstOutTime=OutTime
		oldInOctets=InOctets
		oldOutOctets=OutOctets
		oldInTime=InTime
		oldOutTime=OutTime
		time.sleep(1)

if __name__ == '__main__':
  main()

