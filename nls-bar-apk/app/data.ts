export type Course = {
  id: string;
  name: string;
  short: string;
  description: string;
  accent: string;
};

export const courses: Course[] = [
  { id:'civil', name:'Civil Litigation', short:'CIV', description:'Procedure, evidence, appeals and enforcement', accent:'#1D4ED8' },
  { id:'criminal', name:'Criminal Litigation', short:'CRIM', description:'Criminal procedure, trial practice and sentencing', accent:'#B91C1C' },
  { id:'corporate', name:'Corporate Law Practice', short:'CORP', description:'Companies, securities, transactions and compliance', accent:'#6D28D9' },
  { id:'property', name:'Property Law Practice', short:'PROP', description:'Land transactions, leases, mortgages and perfection', accent:'#047857' },
  { id:'ethics', name:'Professional Ethics', short:'ETH', description:'Professional responsibility, accounts and discipline', accent:'#B45309' },
];

export type Question = {
  id: string;
  course: string;
  stem: string;
  opts: string[];
  correct: number;
  exp: string;
};

export const questionBank: Question[] = [
  {
    id:'civil-1', course:'Civil Litigation',
    stem:'A court acts without subject-matter jurisdiction. Which statement best reflects the orthodox procedural consequence?',
    opts:['The defect is cured by consent','The proceedings are liable to be treated as a nullity','The defect matters only on appeal','The defendant must first admit the claim'],
    correct:1,
    exp:'Subject-matter jurisdiction is foundational. Parties cannot confer jurisdiction on a court by consent.'
  },
  {
    id:'civil-2', course:'Civil Litigation',
    stem:'Which practice habit best protects a candidate against losing marks on a procedural essay?',
    opts:['State the conclusion only','Identify the issue, governing rule, procedure and consequence','Quote every section from memory','Avoid applying facts until the final paragraph'],
    correct:1,
    exp:'A strong procedural answer connects the issue to the governing rule, required steps and legal consequence.'
  },
  {
    id:'criminal-1', course:'Criminal Litigation',
    stem:'In an examination problem, what should you do first when a criminal procedure question turns on the court before which the charge was filed?',
    opts:['Assume jurisdiction','Identify the offence, enabling law and jurisdictional basis','Discuss sentence first','Skip procedure and discuss evidence only'],
    correct:1,
    exp:'Jurisdiction and the statutory basis for the charge should be tested before moving to later trial steps.'
  },
  {
    id:'corporate-1', course:'Corporate Law Practice',
    stem:'A good transaction-law answer should ordinarily distinguish which two matters?',
    opts:['Commercial desirability and handwriting','Corporate authority and regulatory approval','Font choice and page count','Client preference and court dress'],
    correct:1,
    exp:'Corporate authority and external regulatory approval are separate legal questions and may require different steps.'
  },
  {
    id:'property-1', course:'Property Law Practice',
    stem:'When analysing title for a land transaction, which sequence is most useful?',
    opts:['Price, colour, address','Root of title, capacity, encumbrances and perfection requirements','Negotiation, litigation, sentencing','Offer, acceptance and criminal charge'],
    correct:1,
    exp:'A title analysis should test the root of title, the vendor’s capacity, encumbrances and applicable perfection steps.'
  },
  {
    id:'ethics-1', course:'Professional Ethics',
    stem:'Where a professional-conduct question presents a conflict between client instructions and a mandatory professional rule, which should guide the answer?',
    opts:['The client instruction always prevails','The mandatory professional obligation','The cheapest option','The most popular option'],
    correct:1,
    exp:'A lawyer cannot contract out of mandatory professional obligations merely because a client requests otherwise.'
  },
  {
    id:'exam-1', course:'Mixed Practice',
    stem:'During strict examination mode, when should correctness and explanations first become visible?',
    opts:['Immediately after each answer','After every five questions','Only after final submission or time expiry','Whenever a question is flagged'],
    correct:2,
    exp:'Strict examination mode should withhold correctness feedback until the attempt ends.'
  },
  {
    id:'exam-2', course:'Mixed Practice',
    stem:'Which control most directly helps identify a dangerous misconception?',
    opts:['Study streak','Confidently-wrong classification','Theme selector','Bookmark count'],
    correct:1,
    exp:'A confidently wrong answer reveals an incorrect belief rather than a mere guess and is useful for targeted revision.'
  }
];

export const getQuestions = (course?: string) => {
  if (!course || course === 'Mixed Practice') return questionBank;
  const filtered = questionBank.filter(q => q.course === course);
  return filtered.length ? filtered : questionBank;
};