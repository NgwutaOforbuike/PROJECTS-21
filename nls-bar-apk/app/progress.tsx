import React from 'react';
import { ScrollView, View, Text, StyleSheet, Pressable } from 'react-native';
import { router } from 'expo-router';
import { courses } from './data';

export default function Progress(){
  return (
    <ScrollView contentContainerStyle={s.page}>
      <Text style={s.eyebrow}>PROGRESS</Text>
      <Text style={s.title}>Revision dashboard</Text>
      <Text style={s.sub}>This screen is ready to become your performance history once persistent storage is connected.</Text>
      <View style={s.summary}>
        <View><Text style={s.big}>5</Text><Text style={s.small}>Courses</Text></View>
        <View style={s.divider}/>
        <View><Text style={s.big}>—</Text><Text style={s.small}>Average</Text></View>
        <View style={s.divider}/>
        <View><Text style={s.big}>—</Text><Text style={s.small}>Attempts</Text></View>
      </View>
      <Text style={s.section}>Course readiness</Text>
      {courses.map(c=>(
        <View key={c.id} style={s.row}>
          <View style={[s.dot,{backgroundColor:c.accent}]}/>
          <View style={{flex:1}}>
            <Text style={s.course}>{c.name}</Text>
            <Text style={s.pending}>Complete an attempt to establish a baseline</Text>
          </View>
          <Text style={s.percent}>—</Text>
        </View>
      ))}
      <Pressable style={s.primary} onPress={()=>router.push('/courses')}><Text style={s.primaryText}>Start a baseline test</Text></Pressable>
    </ScrollView>
  );
}
const s=StyleSheet.create({
  page:{padding:20,paddingBottom:44,gap:14,backgroundColor:'#F6F7FB'},
  eyebrow:{fontSize:12,fontWeight:'800',letterSpacing:1.4,color:'#2563EB',marginTop:8},
  title:{fontSize:30,fontWeight:'900',color:'#101828'},
  sub:{fontSize:15,lineHeight:22,color:'#667085'},
  summary:{backgroundColor:'#101828',borderRadius:20,padding:22,flexDirection:'row',justifyContent:'space-between',alignItems:'center',marginVertical:4},
  big:{color:'#fff',fontSize:24,fontWeight:'900',textAlign:'center'},small:{color:'#98A2B3',fontSize:11,marginTop:2},
  divider:{width:1,height:34,backgroundColor:'#344054'},
  section:{fontSize:17,fontWeight:'800',color:'#101828',marginTop:8},
  row:{backgroundColor:'#fff',borderRadius:15,padding:15,flexDirection:'row',alignItems:'center',gap:12,borderWidth:1,borderColor:'#EAECF0'},
  dot:{width:10,height:10,borderRadius:5},course:{fontWeight:'800',color:'#101828'},pending:{fontSize:11,color:'#98A2B3',marginTop:3},percent:{fontWeight:'900',color:'#667085'},
  primary:{marginTop:6,padding:16,borderRadius:14,backgroundColor:'#2563EB'},primaryText:{color:'#fff',fontWeight:'800',textAlign:'center'}
});