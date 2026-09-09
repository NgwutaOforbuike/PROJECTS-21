import React from 'react';
import { ScrollView, View, Text, StyleSheet } from 'react-native';

export default function About(){
  return <ScrollView contentContainerStyle={s.page}>
    <Text style={s.eyebrow}>NLS BAR FINALS</Text>
    <Text style={s.title}>Built for disciplined exam practice</Text>
    <Text style={s.sub}>A mobile-first Nigerian Law School revision companion designed around the five Bar Finals courses.</Text>
    {[
      ['Strict exam feedback','Answers are recorded during an attempt, but correctness and explanations stay hidden until submission.'],
      ['Focused and mixed practice','Open a single course or practise across the whole curriculum from one dashboard.'],
      ['Flag and review','Mark uncertain questions, see unanswered counts and make a final review before submitting.'],
      ['Performance layer','The progress interface is prepared for persistent attempt history and weak-area analytics.']
    ].map(([h,b])=><View key={h} style={s.card}><Text style={s.h}>{h}</Text><Text style={s.b}>{b}</Text></View>)}
    <Text style={s.note}>Question content in this build is a starter bank. It should be expanded and validated against the complete Nigerian Law School materials before high-stakes use.</Text>
  </ScrollView>
}
const s=StyleSheet.create({page:{padding:20,paddingBottom:44,gap:14,backgroundColor:'#F6F7FB'},eyebrow:{fontSize:12,fontWeight:'800',letterSpacing:1.4,color:'#2563EB',marginTop:8},title:{fontSize:30,lineHeight:36,fontWeight:'900',color:'#101828'},sub:{fontSize:15,lineHeight:22,color:'#667085',marginBottom:4},card:{backgroundColor:'#fff',borderRadius:16,padding:17,borderWidth:1,borderColor:'#EAECF0',gap:5},h:{fontSize:16,fontWeight:'800',color:'#101828'},b:{fontSize:13,lineHeight:19,color:'#667085'},note:{fontSize:12,lineHeight:18,color:'#7F1D1D',backgroundColor:'#FEF2F2',padding:15,borderRadius:14,marginTop:4}});