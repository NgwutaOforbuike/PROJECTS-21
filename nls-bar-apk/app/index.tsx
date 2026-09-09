import React from 'react';
import { ScrollView, View, Text, Pressable, StyleSheet } from 'react-native';
import { router } from 'expo-router';
const courses=['Civil Litigation','Criminal Litigation','Corporate Law Practice','Property Law Practice','Professional Ethics'];
export default function Home(){
 return <ScrollView contentContainerStyle={s.page}>
  <Text style={s.title}>Bar Finals Command Centre</Text>
  <Text style={s.sub}>Nigerian Law School Bar Finals Practice</Text>
  <View style={s.grid}>{courses.map(c=><Pressable key={c} style={s.card} onPress={()=>router.push({pathname:'/practice',params:{course:c}})}><Text style={s.cardTitle}>{c}</Text><Text>Practice · Mock · Essay · Drafting · Weak Areas</Text></Pressable>)}</View>
  <Pressable style={s.primary} onPress={()=>router.push('/practice')}><Text style={s.primaryText}>Start Mixed Practice</Text></Pressable>
 </ScrollView>
}
const s=StyleSheet.create({page:{padding:24,gap:18},title:{fontSize:30,fontWeight:'800'},sub:{fontSize:16,opacity:.72},grid:{gap:12},card:{padding:18,borderWidth:1,borderColor:'#d7d7d7',borderRadius:14},cardTitle:{fontSize:19,fontWeight:'700',marginBottom:6},primary:{padding:16,borderRadius:12,backgroundColor:'#111'},primaryText:{color:'#fff',fontWeight:'700',textAlign:'center'}});