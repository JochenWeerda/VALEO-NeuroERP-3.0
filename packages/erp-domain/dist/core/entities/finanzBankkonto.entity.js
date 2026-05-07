"use strict";
/**
 * FinanzBankkonto domain entity generated from CRM migration toolkit.
 * Keep the structure focused on pure data/behavior, no infrastructure here.
 */
Object.defineProperty(exports, "__esModule", { value: true });
exports.FinanzBankkonto = void 0;
class FinanzBankkonto {
    constructor(props) {
        this.props = props;
    }
    static create(props) {
        return new FinanzBankkonto(props);
    }
    get id() {
        return this.props.id;
    }
    get kontoname() {
        return this.props.kontoname;
    }
    get bankname() {
        return this.props.bankname;
    }
    get iban() {
        return this.props.iban;
    }
    get bic() {
        return this.props.bic;
    }
    get kontonummer() {
        return this.props.kontonummer;
    }
    get blz() {
        return this.props.blz;
    }
    get waehrung() {
        return this.props.waehrung;
    }
    get kontostand() {
        return this.props.kontostand;
    }
    get letzterAbgleich() {
        return this.props.letzter_abgleich;
    }
    get istAktiv() {
        return this.props.ist_aktiv;
    }
    get notizen() {
        return this.props.notizen;
    }
    get erstelltVon() {
        return this.props.erstellt_von;
    }
    get erstelltAm() {
        return this.props.erstellt_am;
    }
    get aktualisiertAm() {
        return this.props.aktualisiert_am;
    }
    toPrimitives() {
        return { ...this.props };
    }
}
exports.FinanzBankkonto = FinanzBankkonto;
//# sourceMappingURL=finanzBankkonto.entity.js.map