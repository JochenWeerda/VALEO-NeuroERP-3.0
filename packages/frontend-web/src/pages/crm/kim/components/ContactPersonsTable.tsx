/**
 * @license
 * SPDX-License-Identifier: Apache-2.0
 */

import React, { useState } from 'react';
import { ContactPerson } from '../types';
import { Phone, Mail, Calendar, UserCheck, Plus, X, Check, Star } from 'lucide-react';

interface ContactPersonsTableProps {
  contactPersons: ContactPerson[];
  onAddContactPerson: (vals: Partial<ContactPerson>) => void;
}

export default function ContactPersonsTable({ contactPersons, onAddContactPerson }: ContactPersonsTableProps) {
  const [showAddForm, setShowAddForm] = useState(false);
  const [salutation, setSalutation] = useState('Herr');
  const [firstName, setFirstName] = useState('');
  const [lastName, setLastName] = useState('');
  const [position, setPosition] = useState('');
  const [phone1, setPhone1] = useState('');
  const [phone2, setPhone2] = useState('');
  const [fax, setFax] = useState('');
  const [priority, setPriority] = useState(2); // Default priority
  const [birthdate, setBirthdate] = useState('');
  const [isDecisionMaker, setIsDecisionMaker] = useState(true);
  const [schedule, setSchedule] = useState<boolean[]>(Array(10).fill(false));

  const handleToggleSchedule = (idx: number) => {
    const updated = [...schedule];
    updated[idx] = !updated[idx];
    setSchedule(updated);
  };

  const handleFormSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!lastName) return;

    onAddContactPerson({
      salutation,
      name: lastName,
      firstName,
      position,
      phone1,
      phone2: phone2 || undefined,
      fax: fax || undefined,
      priority,
      birthdate: birthdate || undefined,
      weeklySchedule: schedule
    });

    // Reset Form
    setFirstName('');
    setLastName('');
    setPosition('');
    setPhone1('');
    setPhone2('');
    setFax('');
    setPriority(2);
    setBirthdate('');
    setIsDecisionMaker(true);
    setSchedule(Array(10).fill(false));
    setShowAddForm(false);
  };

  return (
    <div className="bg-white border border-[#cbd5e1] rounded-sm shadow-sm overflow-hidden select-none font-sans" id="contact-persons-table-component">
      
      {/* Title bar strip */}
      <div className="bg-[#cbd5e1] border-b border-[#94a3b8] px-3 py-1 flex justify-between items-center">
        <div className="flex items-center gap-1.5 font-bold text-gray-800 text-[11px] uppercase tracking-wider font-mono">
          <UserCheck size={13} className="text-[#006633] fill-[#006633]" />
          <span>Ansprechpartner / Anbauleitung ({contactPersons.length})</span>
        </div>
        
        <button
          onClick={() => setShowAddForm(!showAddForm)}
          className="flex items-center gap-1 px-2.5 py-0.5 border border-[#85929E] rounded-sm font-mono text-[10px] font-bold bg-[#f1f5f9] hover:bg-white text-gray-800 cursor-pointer transition select-none"
        >
          {showAddForm ? <X size={11} /> : <Plus size={11} />}
          <span>{showAddForm ? 'Schließen' : 'Neuer Kontakt +'}</span>
        </button>
      </div>

      {/* L3 Compact Insertion Form Row */}
      {showAddForm && (
        <form onSubmit={handleFormSubmit} className="p-3 bg-slate-50 border-b border-[#cbd5e1] grid grid-cols-12 gap-2 text-[11px] font-sans" id="inline-cp-insert-form">
          <div className="col-span-6 md:col-span-1">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Anrede</label>
            <select
              value={salutation}
              onChange={e => setSalutation(e.target.value)}
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 text-[11px] font-semibold"
            >
              <option value="Herr">Herr</option>
              <option value="Frau">Frau</option>
              <option value="Firma">Firma</option>
            </select>
          </div>

          <div className="col-span-6 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Vorname</label>
            <input
              type="text"
              value={firstName}
              onChange={e => setFirstName(e.target.value)}
              placeholder="z.B. Eimo"
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 text-[11px]"
            />
          </div>

          <div className="col-span-6 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Nachname/Name</label>
            <input
              type="text"
              required
              value={lastName}
              onChange={e => setLastName(e.target.value)}
              placeholder="z.B. de Buhr"
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 text-[11px] font-extrabold"
            />
          </div>

          <div className="col-span-6 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Position / Verantwortung</label>
            <input
              type="text"
              value={position}
              onChange={e => setPosition(e.target.value)}
              placeholder="z.B. Gutsverwalter"
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 text-[11px]"
            />
          </div>

          <div className="col-span-6 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Telefon 1</label>
            <input
              type="text"
              required
              value={phone1}
              onChange={e => setPhone1(e.target.value)}
              placeholder="Durchwahl"
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 text-[11px]"
            />
          </div>

          <div className="col-span-6 md:col-span-1">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Prio</label>
            <input
              type="number"
              min="1"
              max="9999"
              value={priority}
              onChange={e => setPriority(Number(e.target.value))}
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 font-mono text-[11px]"
            />
          </div>

          <div className="col-span-12 md:col-span-2">
            <label className="block text-[9px] text-[#475569] font-bold uppercase mb-0.5 font-mono">Geburtsdatum</label>
            <input
              type="date"
              value={birthdate}
              onChange={e => setBirthdate(e.target.value)}
              className="w-full bg-white border border-[#94a3b8] rounded px-1.5 py-0.5 text-[10px]"
            />
          </div>

          {/* Logistics weekly schedules and save block */}
          <div className="col-span-12 flex flex-col md:flex-row items-center gap-4.5 pt-2 border-t border-dashed border-[#94a3b8] justify-between">
            <div className="flex flex-wrap items-center gap-1.5 pb-1">
              <span className="text-[9.5px] font-bold text-gray-500 uppercase leading-none mr-2 font-mono">Wochenplanung (Erreichbarkeit W1-W10):</span>
              <div className="flex gap-0.5">
                {Array(10).fill(0).map((_, i) => (
                  <button
                    key={i}
                    type="button"
                    onClick={() => handleToggleSchedule(i)}
                    className={`w-5 h-5 text-[9px] font-mono leading-none rounded-sm border cursor-pointer select-none font-bold transition-all ${
                      schedule[i] ? 'bg-[#006633] text-white border-transparent' : 'bg-white border-gray-300 text-gray-400 hover:bg-gray-100'
                    }`}
                  >
                    {i+1}
                  </button>
                ))}
              </div>
            </div>

            <button
              type="submit"
              className="bg-[#006633] hover:bg-emerald-800 text-white font-bold font-mono text-[10px] px-4.5 py-1.5 rounded-sm flex items-center gap-1 cursor-pointer transition select-none uppercase shadow-sm self-end"
            >
              <Check size={11} className="stroke-[3]" />
              <span>Sichern [F11]</span>
            </button>
          </div>
        </form>
      )}

      {/* Strict Tabular High Density Matrix */}
      <div className="overflow-x-auto">
        <table className="w-full text-left font-mono text-[11px] border-collapse bg-white leading-none">
          <thead>
            <tr className="bg-[#cbd5e1] border-b border-[#94a3b8] text-gray-700 select-none font-extrabold text-[10px]">
              <th className="p-2 border-r border-[#cbd5e1] w-12 font-sans uppercase">Anrede</th>
              <th className="p-2 border-r border-[#cbd5e1] md:w-32 font-sans uppercase">Name</th>
              <th className="p-2 border-r border-[#cbd5e1] md:w-32 font-sans uppercase">Vorname</th>
              <th className="p-2 border-r border-[#cbd5e1] font-sans uppercase">Position / Verantwortlichkeit</th>
              <th className="p-2 border-r border-[#cbd5e1] text-center w-12 font-sans uppercase">Prio</th>
              <th className="p-2 border-r border-[#cbd5e1] text-center w-20 font-sans uppercase">Geburstdatum</th>
              <th className="p-2 border-r border-[#cbd5e1] w-24 font-sans uppercase">Telefon 1</th>
              <th className="p-2 border-r border-[#cbd5e1] w-24 font-sans uppercase">Telefon 2 / Mobil</th>
              <th className="p-2 border-r border-[#cbd5e1] text-center w-14 font-sans uppercase">Entscheid</th>
              {/* W1-W10 Headers */}
              <th className="p-2 text-center bg-emerald-50 text-emerald-800 border-l border-[#85929E]" colSpan={10}>
                Lieferplan-Rotation (W1 bis W10)
              </th>
            </tr>
          </thead>
          <tbody>
            {contactPersons.length === 0 ? (
              <tr className="border-b border-[#cbd5e1]">
                <td colSpan={19} className="p-6 text-center text-gray-400 font-sans font-semibold italic">
                  Keine zugeordneten Kontakt-Partner im System hinterlegt.
                </td>
              </tr>
            ) : (
              contactPersons.map((person) => (
                <tr key={person.id} className="border-b border-[#cbd5e1] hover:bg-[#f0f9ff]/50 transition text-[11px]" id={`cp-row-${person.id}`}>
                  <td className="p-1.5 border-r border-[#cbd5e1] font-sans font-semibold text-gray-500">{person.salutation}</td>
                  <td className="p-1.5 border-r border-[#cbd5e1] font-sans font-black text-[#0f172a]">{person.name}</td>
                  <td className="p-1.5 border-r border-[#cbd5e1] font-sans font-bold text-gray-700">{person.firstName}</td>
                  <td className="p-1.5 border-r border-[#cbd5e1] font-sans font-semibold">
                    <span className="bg-slate-100 text-slate-800 px-1.5 py-0.5 rounded-sm border border-slate-200">
                      {person.position || 'Anbauleitung'}
                    </span>
                  </td>
                  <td className="p-1.5 border-r border-[#cbd5e1] text-center font-bold text-slate-600">
                    <span className={`px-1 rounded-sm text-[9px] ${person.priority === 1 ? 'bg-red-100 text-red-800 font-black' : 'bg-gray-100 text-gray-600'}`}>
                      {person.priority}
                    </span>
                  </td>
                  <td className="p-1.5 border-r border-[#cbd5e1] text-center text-gray-500 whitespace-nowrap">
                    {person.birthdate ? (
                      <span className="flex items-center justify-center gap-1 font-semibold text-[10px] font-mono">
                        <Calendar size={10} className="text-gray-400" />
                        {new Date(person.birthdate).toLocaleDateString("de-DE")}
                      </span>
                    ) : '—'}
                  </td>
                  <td className="p-1.5 border-r border-[#cbd5e1]">
                    {person.phone1 ? (
                      <a href={`tel:${person.phone1}`} className="text-[#006633] hover:underline font-extrabold flex items-center gap-1 font-mono" title="Klicken um anzurufen (Zentrale)">
                        <Phone size={9} className="text-[#006633]" />
                        <span>{person.phone1}</span>
                      </a>
                    ) : '—'}
                  </td>
                  <td className="p-1.5 border-r border-[#cbd5e1]">
                    {person.phone2 ? (
                      <a href={`tel:${person.phone2}`} className="text-blue-700 hover:underline font-extrabold flex items-center gap-1 font-mono" title="Klicken: Mobilfunknetz">
                        <Phone size={9} className="text-blue-600" />
                        <span>{person.phone2}</span>
                      </a>
                    ) : <span className="text-gray-400">—</span>}
                  </td>
                  <td className="p-1.5 border-r border-[#cbd5e1] text-center font-bold text-emerald-700">
                    <span className="bg-[#e2f0d9] text-[#2e7d32] border border-[#a9d18e] px-1 rounded-sm text-[9px]">EN</span>
                  </td>
                  
                  {/* Output W1-W10 exact flags */}
                  {Array(10).fill(0).map((_, idx) => {
                    const isWeekActive = person.weeklySchedule && person.weeklySchedule[idx];
                    return (
                      <td
                        key={idx}
                        className={`p-1 border-r ${
                          idx === 0 ? 'border-l border-[#85929E]' : 'border-[#cbd5e1]'
                        } text-center ${isWeekActive ? 'bg-[#e2f0d9]/35' : 'bg-white'}`}
                      >
                        <div className="flex justify-center items-center">
                          <span 
                            className={`w-3.5 h-3.5 rounded text-[8px] font-mono font-extrabold flex items-center justify-center border ${
                              isWeekActive 
                                ? 'bg-[#006633] text-white border-transparent shadow-sm' 
                                : 'bg-slate-50 border-gray-200 text-gray-300'
                            }`}
                            title={`Lieferzeitfenster Woche: ${idx+1}`}
                          >
                            {idx + 1}
                          </span>
                        </div>
                      </td>
                    );
                  })}
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>

    </div>
  );
}
