"""Narrow, reversible Korean compact-note typing patch.

Only the token splitter and two help labels change. Pitch/duration parsing,
hand assignment at insertion, validation, undo and saving stay in the original.
A compact chunk is split only when EVERY character belongs to valid tokens.
English tokens retain the original whitespace requirement and flat-b meaning.
"""
OLD_LEXER = r"function parseNoteText(text,baseBeats){ const toks=text.replace(/[,，]/g,' ').split(/\s+/).filter(Boolean);"
NEW_LEXER = r"""function parseNoteText(text,baseBeats){
  // PIANO_COMPACT_KOREAN_NOTES_V1: keep the original parser after tokenization.
  const toks=text.replace(/[,，]/g,' ').split(/\s+/).filter(Boolean).flatMap(raw=>{
    // English stays explicit: 'ab' is A-flat, NOT a newly inferred A then B.
    if(!/[도레미파솔라시쉼]/.test(raw)) return [raw];
    const parts=raw.match(/(?:[도레미파솔라시][#♯b♭]?\d?[\^v]*-*\/*|(?:쉼|_|\.|[rR])-*\/?)/g);
    // Never drop typos or unknown text; the existing dialog rejects bad input.
    return parts && parts.join('')===raw ? parts : [raw];
  });"""
OLD_HELP = '계이름을 띄어쓰기로 적으세요.'
NEW_HELP = '한글 계이름은 붙여 쓰거나 띄어 써도 돼요 (도도솔솔 · 도 도 솔 솔). 영어 음이름은 공백으로 나눠 주세요.'
EDITS = ((OLD_LEXER, NEW_LEXER), (OLD_HELP, NEW_HELP), ('한 글자 길이 <select id="teLen"', '한 음 길이 <select id="teLen"'))

def apply(text):
    """Fail closed if the reviewed anchors have changed or are already patched."""
    original = text
    changes = []
    for old, new in EDITS:
        if text.count(old) != 1 or new in text:
            raise ValueError('Typed-note source differs from the reviewed version: ' + old[:75])
        text = text.replace(old, new, 1)
        changes.append({'old':old, 'new':new, 'count':1})
    recovered = text
    for c in reversed(changes):
        recovered = recovered.replace(c['new'], c['old'], 1)
    if recovered != original:
        raise AssertionError('Typed-note patch did not recover source exactly.')
    return text, changes
